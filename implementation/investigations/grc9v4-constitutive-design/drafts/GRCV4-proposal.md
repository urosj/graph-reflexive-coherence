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

The tranche reorganizes accepted results for exposition; it does not derive a second GRC-v4, modify an accepted equation, promote an unresolved claim, or authorize implementation. Claim associations in the crosswalk preserve the explorer disposition `indeterminate_requires_review`; they are provenance references rather than reconstructed support proof. A source-local provenance identifier is not assumed to be a queryable claim node or graph edge merely because an accepted audit record names it.

### Coverage and status corrections applied in this tranche

A literal parent-object coverage pass over the extraction skeleton found four D10.2 parent identifiers without an extraction slot. This tranche closes those drafting gaps as follows:

| Previously absent parent object | New extraction location | Treatment |
|---|---|---|
| `BASE-SCALAR-MOBILITY` | §4.1 | Positive scalar edge-mobility input of the inherited baseline transport channel |
| `BASE-POTENTIAL` | §4.1 | Graph-generic potential equation |
| `BASE-POTENTIAL-FLOW` | §4.1 | Oriented potential-flow equation and its separation from retained/total current |
| `SPEC-VERIFICATION-REGISTRY` | §2.5 | Separation of scientific claim topology from runtime, numerical, and implementation verification |

When these insertions are merged into the controlling skeleton, all 67 D10.2 parent normative objects are present by identifier.

One claim-status correction is also made explicit. The D10 preclosure condition `D10-CL-C-011` is not carried forward as an unresolved generic-substrate question. The accepted D10.2 audit records, at `/claim_topology_effect/D10_conditional_claim_D10_CL_C_011`, that it is `succeeded_by_accepted_D10_2_CL_N_001`; the adjacent `/claim_topology_effect/D10_2_CL_N_001` value records the bounded factorization earned for the current D10 initial population. `D10_2_CL_N_001` is a source-local provenance label in that audit record, not a queryable `current_claim`, `normative_object`, or `equation_contract` node and not a graph-resolved successor edge. The accepted record-level status update earns the bounded factorization

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
| §2.1.1, §3.1, §3.3 | `CORE-C-AUTHORITY` | `D10.2-EC-PARENT-CORE-C-AUTHORITY` | `D10-CL-N-001`, `D10-CL-N-002`; bounded generic promotion recorded by the non-node D10.2 provenance label `D10_2_CL_N_001` |
| §2.1.2, §3.4 | `BASE-GRC-DIFFERENTIAL` | `D10.2-EC-PARENT-BASE-GRC-DIFFERENTIAL` | `D10-CL-N-001`; graph-generic promotion accepted |
| §4.1.1 | `BASE-SCALAR-MOBILITY` | `D10.2-EC-PARENT-BASE-SCALAR-MOBILITY` | `D10-CL-N-001`; D10.2 `/claim_topology_effect` records the predecessor `D10-CL-C-011` status update under non-node provenance label `D10_2_CL_N_001` |
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
| Generic-substrate promotion | Closed bounded by the accepted D10.2 audit's `claim_topology_effect`; `D10_2_CL_N_001` is its non-node provenance label | No | Reopen only for a materially distinct future profile outside the audited population |
| Future-exhaustive profile taxonomy | Not established; `D10-CL-C-012` remains the ceiling | No | Only if the proposal attempts to claim that the ten current profiles exhaust all lawful GRC-v4 constructions |

**Current disposition:** Sections 2–4 are fillable from the accepted investigation. They expose no new scientific contradiction and require no successor investigation.

### Sections 5–7 tranche status

**Status:** Working synthesis from the accepted GRC-v4/GRC9V4 constitutive-design investigation.

**Scientific authority:** None independent of the accepted investigation.

**Current controlling closure:** Accepted D10.2, decision digest `28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c`.

The tranche reorganizes accepted results for exposition; it does not derive a second GRC-v4, alter an accepted equation, promote an unresolved claim, or authorize implementation. All 22 queried equation/contract associations retain the explorer disposition `indeterminate_requires_review`; the crosswalk records source relationships rather than reconstructed support proof.

### Coverage and status controls applied in this tranche

This tranche preserves several distinctions that are easy to lose when the chronological investigation is reorganized as a substrate account.

| Pressure point | Treatment in Sections 5–7 |
|---|---|
| A role-level retained object could be mistaken for one universal serialized state | §5.1 treats $T_M$ as a causal role only; profile authority is left to A, C, and realization-specific history contracts |
| Baseline potential flow, explicit Read-Back current, structural one-form current, and authoritative resource current could collapse into one symbol | §§5.3–5.4 and §§6.2–6.4 keep $J_0$, $j$, $j_{\mathrm{struct}}^\flat$, and $J_C$ separately typed |
| The historical D7G lagged-explicit geometry gap could be carried forward as if it remained the common V4 architecture | §6 states the accepted geometry map independently of temporal realization; CI, OS, RG2b, PC, and CI+PC own the causal-consumption timing developed in Section 10 |
| $H_{1,\mathrm{form}}$, $G_J$, $M_4$, $K_4$, and $h_4$ could be merged by equal dimensions or coincident reference arrays | §6 gives each object a distinct type, domain, authority, and causal role |
| The ten admitted profiles could be presented as a universal taxonomy | §7.1 calls them the complete current initial population and preserves `D10-CL-C-012` as the future-exhaustiveness boundary |
| Claim governance could be treated as runtime state or as a mandatory linear research backlog | §§7.3 and 7.5 keep claim topology, successor admission, and verification obligations as specification-meta contracts |
| Candidate B could be silently filled by PC or by an invented carrier equation | §7.4 preserves B as routed, unrejected, nonexecutable, and without a source-backed writer |

`D10-CL-C-011` is no longer an outstanding generic-substrate preclosure condition for the current population. The accepted D10.2 audit records the bounded status update in `/claim_topology_effect` under the non-node provenance label `D10_2_CL_N_001`. That record-level promotion does not alter the historical graph node or the status of open runtime, stability, attribution, ranking, dimensionalization, or future-profile claims.


### Sections 5–7 provenance crosswalk

The table below is a drafting-control surface. It does not replace the D10.2 registry or the accepted predecessor records.

| Proposal location | Parent object(s) | Equation/contract row(s) | Current claim relation |
|---|---|---|---|
| §5.1, §5.3, §5.4 | `L-AUTHORITATIVE-CURRENT`, `A-READ-CLOSURE`, `C-READ-BACK` | `D10.2-EC-PARENT-L-AUTHORITATIVE-CURRENT`, `D10.2-EC-PARENT-A-READ-CLOSURE`, `D10.2-EC-C-RESOLVENT`, `D10.2-EC-C-READBACK` | `D10-CL-N-003`; A/C optional profiles; physical nonabsorbability remains conditional |
| §5.2, §5.5 | `A-RETAINED-WRITER`, `A-WRITER-TARGET`, `C-AUTHORITY`, `REAL-PC`, `L-POSTCONTINUITY-REFRESH` | parent rows plus `D10.2-EC-PC-WRITER-COEFFICIENT`, `D10.2-EC-PC-ZOH-WRITER`, `D10.2-EC-PC-RELEASE` | A/C/PC optional claims; runtime formation/retention remains open |
| §5.6 | candidate read/write parents, `L-SINGULAR-FAIL-CLOSED`, disabled-surface parents | D5/D7 control contracts and D10.2 parent/disabled rows | null and control surfaces remain noninterchangeable; exact disabled reductions belong to GRC9V4 specialization |
| §6.1 | `CORE-K-STRUCTURAL-ROLE`, `GEOM-K4`, `GEOM-ASSEMBLY` | corresponding parent rows plus `D10.2-EC-GEOM-K4-ASSEMBLY` | `D10-CL-N-006`; normalization uniqueness remains open |
| §6.2 | `GEOM-H1-FORM`, `GEOM-GJ` | `D10.2-EC-PARENT-GEOM-H1-FORM`, `D10.2-EC-PARENT-GEOM-GJ`, `D10.2-EC-GEOM-FLAT` | accepted Hodge correction; general-SPD runtime conformance remains conditional |
| §6.3 | `GEOM-H1-FORM`, `GEOM-GJ`, `GEOM-K4-TO-H4-TO-h4` | `D10.2-EC-GEOM-HODGE-UPDATE`, `D10.2-EC-GEOM-FLAT`, `D10.2-EC-GEOM-PROFILE` | `D10-CL-N-006`; current affine profile is admitted, not unique |
| §6.4 | `GEOM-M4` | `D10.2-EC-PARENT-GEOM-M4`, `D10.2-EC-GEOM-MOBILITY-BOUNDARY` | geometry/mobility authority separation is normative for current population |
| §6.5 | `GEOM-COVARIANCE` | `D10.2-EC-PARENT-GEOM-COVARIANCE` | form-level covariance accepted; executable and event transport obligations remain separately gated |
| §7.1 | `L-PROFILE-GRAMMAR`, `SPEC-PROFILE-GRAMMAR` | corresponding parent rows | `D10-CL-N-009`; lifecycle binding `D10-CL-N-005`; `D10-CL-C-012` blocks a future-exhaustive roster claim |
| §7.2 | `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`, `SPEC-COMPOSITION-PROFILE-IDENTITY` | corresponding parent rows | `D10-CL-N-008`; changed gain or mathematical contract requires new identity |
| §7.3 | `SPEC-FUTURE-ADMISSION` | `D10.2-EC-PARENT-SPEC-FUTURE-ADMISSION` | current promotion is bounded; successors reopen provenance and earliest affected contract |
| §7.4 | `SPEC-B-SLOT` | `D10.2-EC-PARENT-SPEC-B-SLOT` | B is open/routed, not rejected; `D10-CL-X-005` blocks PC-as-B |
| §7.5 | `SPEC-CLAIM-CEILINGS`, `SPEC-VERIFICATION-REGISTRY` | corresponding parent rows | claim governance and verification obligations remain distinct from runtime state and design mathematics |


### Paper-pressure register after Sections 5–7

| Boundary | Current disposition | Does it block this tranche? | Successor trigger condition |
|---|---|---|---|
| One universal serialized $T_M$ state | Rejected by profile-specific authority; $T_M$ is a role label | No | Only if the final proposal requires one state coordinate common to A, C, and all realizations |
| One universal solved equation for $J_C=J_0+\zeta j$ | Outer composition is common; root, domain, and staging are profile-specific | No | Only if later prose needs a global uniqueness or common inverse theorem |
| Runtime formation, post-input retention, and release | Design transitions accepted; runtime branch evidence unexecuted | No | Only if the proposal claims demonstrated memory rather than a lawful substrate mechanism |
| Physical nonabsorbability of the explicit read channel | Open for A and C | No | Only if the proposal must state that no baseline reparameterization can reproduce the admitted effect |
| Nonzero committed endpoint effect | Complete-chain consumption does not imply endpoint effect | No | Only if a central paper proposition requires measured or proved endpoint hysteresis |
| Universal or unique $K_4$ assembly normalization | Diagonal overlap multiplicity closed; off-diagonal cover dependence remains | No | Only if the proposal claims canonical or continuum-unique normalization |
| Physical flux used directly as structural one-form | Blocked by accepted Hodge correction | No | Any section that cannot preserve the $G_J$ flat/sharp boundary would require correction, not a new optional profile |
| Geometry automatically determines mobility | Explicitly blocked; no current $h_4\to M_4$ authority map | No | A proposed geometry-conditioned transport law would require a named successor and earliest-contract reopening |
| Current affine Hodge profile as unique $g[K]$ | Explicitly bounded reference profile | No | Only if the proposal claims uniqueness, universality, or continuum identity |
| General-SPD runtime conditioning and covariance | Verification obligation, not unresolved design mathematics | No | Only if the proposal asserts implementation or numerical guarantees |
| Ten-profile roster as exhaustive V4 taxonomy | Blocked by `D10-CL-C-012` | No | Only if the intended paper cannot remain bounded to the current initial population |
| Candidate B as executable or equivalent to PC | B routed but lacks source-backed writer; PC-as-B blocked | No | Only if the paper requires B in the current executable population |
| Fixed successor schedule | Rejected; successors activate at exact attempted claims | No | A successor investigation is required only at a concrete unsupported paper proposition |

**Current disposition:** Sections 5–7 are fillable from the accepted investigation. They expose no new scientific contradiction and require no successor investigation. Candidate-specific equations and realization-specific roots remain intentionally deferred to Sections 8–10 rather than being duplicated in the common causal and profile layers.

---

### Sections 8–10 tranche status

**Status:** Working synthesis from the accepted GRC-v4/GRC9V4 constitutive-design investigation

**Intended use:** Integrated controlled content in `drafts/GRCV4-proposal.md`

**Scientific authority:** None independent of the accepted investigation

**Current controlling closure:** accepted D10.2, decision digest `28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c`

This tranche fills the third drafting tranche identified in the extraction skeleton: Sections 8–10. It begins from the common causal loop, structural geometry, and complete-profile grammar assembled in Sections 5–7. It then gives the accepted candidate-local mathematics for A and C and the accepted realization-local mathematics for CI, OS, RG2b, PC, and CI+PC.

The purpose is not to derive a second GRC-v4. Every equation below is an exposition of an accepted investigation result. Candidate equations remain candidate-specific; realization equations remain realization-specific; accepted local regularity is not enlarged into global existence or stability; and unresolved runtime, attribution, dimensionalization, or preference claims remain outside the content.

The immediate controlling records are:

- `../decisions/D4v2CandidateGeometryAndCarrierCompletion.md` and `.json`;
- `../decisions/D5DirectionalReadBack.md` and `.json`;
- `../decisions/D5v2DirectionalReadBackCompletion.md` and `.json`;
- `../decisions/D6TotalCurrentClosure.md` and `.json`;
- `../decisions/D6v2UpdatedTotalCurrentClosure.md` and `.json`;
- `../decisions/D7ClosedWriteReadLoop.md` and `.json`;
- `../decisions/D7v2CandidateTransitionComparativeAdmission.md` and `.json`;
- `../decisions/D7GGlobalMetricAndStructuralCultivationClosure.md` and `.json`;
- `../decisions/D7Gv2GeometryParametricClosureAndFinalization.md` and `.json`;
- `../decisions/D7GPostv2GraphHodgeTypeCorrection.md` and `.json`;
- `../decisions/GeometryTemporalRealizationSuccessorCoupledImplicit.md` and `.json`;
- `../decisions/D8BCoupledArchitectureLocalContinuationAnalysis.md` and `.json`;
- `../decisions/GeometryTemporalRealizationSuccessorOperatorSplit.md` and `.json`;
- `../decisions/GeometryTemporalRealizationSuccessorReconstructedGeometry.md` and `.json`;
- `../decisions/GeometryTemporalRealizationSuccessorPersistentCarrier.md` and `.json`;
- `../decisions/GeometryTemporalRealizationHybridCoupledPersistentCarrier.md` and `.json`;
- `../decisions/GeometryTemporalRealizationComparativeSynthesis.md` and `.json`;
- `../decisions/D9CompleteStepAndLifecycleContract.md` and the D9 profile/state/lifecycle registry;
- `../decisions/D10DesignSynthesisAndSpecWritingDecision.md` and claim topology;
- `../decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.md` and `.json`.

Earlier theory, substrate, specification, and runtime sources enter only through the lineage accepted by these records. The forensic API audit reconstructed 16 cited or load-bearing claims, queried 21 parent objects, and traced 51 equation/contract rows against the exact admitted source and graph digests. Every contract association retains `indeterminate_requires_review`; the tool cannot provide a missing equation, alter an accepted profile, or resolve a paper boundary.

### Coverage and status controls applied in this tranche

Sections 8–10 are the first tranche in which a prose reorganization can easily create a second mathematical line. The following controls are therefore explicit.

| Pressure point | Treatment in Sections 8–10 |
|---|---|
| Candidate A’s fixed-geometry recurrence and its geometry-consuming realizations could be merged into an invented universal transition | §8 states the accepted A constitutive core; §10 states the realization-specific geometry consumption and root or stage order |
| Candidate A’s retained mobility could be relabeled as structural geometry | $W_A$ remains the sole A mobility authority; $K_4$, $H_{1,\mathrm{form}}$, $G_J$, and $h_4$ remain separately typed |
| Candidate C’s selected sector could be made into an independent hidden state | §9 keeps $C$ as the sole independently written candidate coordinate and rederives all selector, Hodge, resolvent, and read surfaces |
| Historical D5-v2 notation could apply $\chi_C$ twice | §9 uses the final accepted ungated $\widehat R_{C,M}$ and applies $\chi_C$ exactly once to the causal read |
| Exact invertibility in retained coordinates could be misstated as an unchanged physical singular-value margin | §9 transfers exact invertibility by similarity and keeps physical conditioning dependent on the identification condition number |
| CI local branch uniqueness could be restated as global uniqueness or stability | §10.2 admits only the local branch connected to the accepted $\kappa_H=0$ reference |
| OS could be silently iterated until it becomes CI | §10.3 freezes exactly one predictor, one geometry update, one corrector, and one atomic commit |
| RG2b could be treated as an arbitrary reconstruction or a differentiable continuation manifold | §10.4 binds it to the frozen family-local extension and claims only the accepted bounded $C^0$ Lipschitz section |
| PC could be relabeled as Candidate B or as a universal memory law | §10.5 keeps PC as one realization-specific scalar-ZOH $K_4$ carrier crossed with A or C |
| CI+PC could double-count gates or use different structural sources in the immediate and retained paths | §10.6 audits $\chi$, $\zeta$, $\rho_{\mathrm{inst}}$, $\kappa_H$, and $a_{\mathrm{PC}}$ once each and uses one root source for both paths |
| Admitted alternatives could become ranked alternatives | §10.7 compares causal architecture only and preserves the accepted no-ranking disposition |

The profile labels used below are those accepted by D9 and D10. No section claims that the two candidate families or five realization families are future-exhaustive. No equation in this tranche changes the complete-profile identity rules established in §7.

### Sections 8–10 provenance crosswalk

The crosswalk below is a drafting-control surface. The accepted D10.2 registry and predecessor records remain authoritative.

| Proposal location | Parent object(s) | Equation/contract row(s) | Current claim relation |
|---|---|---|---|
| §8.1 | `A-STATE-REDUCTION` | `D10.2-EC-PARENT-A-STATE-REDUCTION` | A is an optional admitted family under `D10-CL-O-001`; not inherited core |
| §8.2 | `BASE-SCALAR-MOBILITY`, `GEOM-M4`, `REAL-CI`, `REAL-OS` | corresponding parent rows plus `D10.2-EC-CI-A-ROOT`, `D10.2-EC-OS-A-CORRECTOR` | inherited scalar transport and candidate-owned mobility remain distinct from realization-specific geometry consumption under `D10-CL-N-001`, `D10-CL-N-006` |
| §8.3 | `A-GW-FUNCTIONAL` | `D10.2-EC-PARENT-A-GW-FUNCTIONAL` | current curvature-disabled profile only; curvature successor reopens provenance |
| §8.4 | `A-WHAT` | `D10.2-EC-PARENT-A-WHAT` | pre-read stage is load-bearing and realization-specific |
| §8.5 | `A-DIRECTIONAL-CONTRAST` | `D10.2-EC-PARENT-A-DIRECTIONAL-CONTRAST` | derived relation, not state or writer |
| §8.6 | `A-READ-CLOSURE` | `D10.2-EC-PARENT-A-READ-CLOSURE` | design-level read sensitivity accepted; physical nonabsorbability remains `D10-CL-C-007` |
| §§8.7, 9.7 | `GEOM-ASSEMBLY`, `REAL-CI` | `D10.2-EC-PARENT-GEOM-ASSEMBLY`, `D10.2-EC-GEOM-K4-ASSEMBLY`, candidate CI root rows | typed candidate structural sources specialize the common assembly; they do not merge current, geometry, and mobility authority |
| §§8.8–8.9 | `A-WRITER-TARGET`, `A-RETAINED-WRITER` | corresponding D10.2 parent rows | complete A writer admitted; runtime formation/retention evidence remains open |
| §9.1, §9.8 | `C-AUTHORITY` | `D10.2-EC-PARENT-C-AUTHORITY`, `D10.2-EC-C-AUTHORITY` | $C$-only authority is normative under `D10-CL-N-002` |
| §9.2 | `C-SECTOR`, `C-SELECTOR` | parent rows and `D10.2-EC-C-SECTOR` | Candidate C admitted under `D10-CL-O-002`; rank/boundary contract remains explicit |
| §§9.3–9.4 | `C-HODGE-MAPS` | `D10.2-EC-PARENT-C-HODGE-MAPS`, `D10.2-EC-C-HODGE-LAPLACIAN` | positive typed Hodge package; matrix shape is not typing |
| §§9.5–9.6 | `C-READ-BACK` | `D10.2-EC-PARENT-C-READ-BACK`, `D10.2-EC-C-RESOLVENT`, `D10.2-EC-C-READBACK` | ungated intrinsic response; $\chi_C$ exactly once; general physical conditioning remains conditional under `D10-CL-C-006` |
| §10.2 | `REAL-CI` | parent row plus `D10.2-EC-CI-A-ROOT`, `D10.2-EC-CI-A-CONTRACTION`, `D10.2-EC-CI-C-ROOT`, `D10.2-EC-CI-C-CONTRACTION`, `D10.2-EC-CI-C-ROOT-SELECTION` | optional realization `D10-CL-O-003`; local branch, not stability |
| §10.3 | `REAL-OS` | parent row plus `D10.2-EC-OS-STAGE-ORDER`, `D10.2-EC-OS-A-CORRECTOR`, `D10.2-EC-OS-C-CORRECTOR`, `D10.2-EC-OS-SPLIT-RESIDUAL`, `D10.2-EC-OS-NO-SECOND-ITERATION` | optional realization `D10-CL-O-004`; one-pass identity is frozen |
| §10.4 | `REAL-RG2B` | parent row plus `D10.2-EC-RG-INVARIANCE`, `D10.2-EC-RG-LIPSCHITZ-CONTRACTION`, `D10.2-EC-RG-DETERMINISM`, `D10.2-EC-RG-CLAIM-CEILING` | optional realization `D10-CL-O-005`; $C^1$ analysis remains conditional under `D10-CL-C-009` |
| §10.5 | `REAL-PC` | parent row plus `D10.2-EC-PC-WRITER-COEFFICIENT`, `D10.2-EC-PC-ZOH-WRITER`, `D10.2-EC-PC-RELEASE`, `D10.2-EC-PC-MATCHED-FORCING` | optional realization `D10-CL-O-006`; `D10-CL-X-005` blocks PC-as-B |
| §10.6 | `REAL-CI-PC`, `SPEC-COMPOSITION-PROFILE-IDENTITY` | corresponding parent rows plus `D10.2-EC-CI-PC-A-COMPOSITION`, `D10.2-EC-CI-PC-A-ROOT`, `D10.2-EC-CI-PC-C-COMPOSITION`, `D10.2-EC-CI-PC-C-CONTRACTION`, `D10.2-EC-CI-PC-C-ROOT-SELECTION`, `D10.2-EC-CI-PC-ABLATIONS` | optional realization `D10-CL-O-007`; gain-two composition is profile identity under `D10-CL-N-008` |
| §§10.7–10.8 | all five realization parents | comparative synthesis and D10 profile grammar | no ranking; `D10-CL-C-012` blocks a future-exhaustive roster claim |


### Paper-pressure register after Sections 8–10

| Boundary | Current disposition | Does it block this tranche? | Successor trigger condition |
|---|---|---|---|
| Candidate A as a universal or inherited RC law | Explicitly blocked; A is one revision-specific admitted family | No | Only if the proposal must claim A is core, unique, or necessary |
| Candidate A physical units and cross-profile magnitude | Current law is normalized and nondimensional | No | If a central comparison requires physical dimensionalization or matched capacity |
| A explicit-read nonabsorbability | Constitutive sensitivity shown; physical nonabsorbability open | No | If the proposal must prove no admissible baseline reparameterization can reproduce the effect |
| Candidate C as independent retained state | Rejected; $T_C$ and Hodge surfaces remain derived from $C$ | No | If later content requires independently serializing or writing $T_C$ |
| C selected-sector recurrence as demonstrated memory | Formal resource-mediated recurrence accepted; runtime post-input evidence absent | No | If the proposal must claim demonstrated retained memory rather than an admitted constitutive mechanism |
| $\chi_C$ placement | Closed by final ungated-resolvent convention | No | Any double-gated formula is a correction to the draft, not a new scientific option |
| C physical inverse margin | Exact invertibility transfers by similarity; norm margin depends on identification conditioning | No | If the proposal requires an unconditional physical norm theorem |
| CI global root or stability | Only local regular branch accepted | No | If the paper’s central result requires global existence, basin size, or stability |
| OS as an approximation converging to CI | One-pass residual and local conditional bounds accepted; no iteration theorem | No | If OS must be justified by global or $\Delta t$ convergence |
| RG2b differentiability and continuation spectrum | Only deterministic bounded Lipschitz section accepted | No | If Section 13 requires a classical derivative of $\Gamma_a$ or an RG spectrum |
| PC endpoint hysteresis | Carrier persistence and matched-forcing contraction accepted; endpoint effect open | No | If the proposal must establish nonzero committed resource or observable hysteresis |
| PC as Candidate B or universal memory | Explicitly blocked | No | If B is required in the current executable population |
| CI+PC amplitude neutrality | False for the accepted unit-plus-unit profile; steady gain is two | No | If a matched-amplitude preference comparison is required |
| CI+PC source identity | Same root source required for immediate and retained paths | No | A need for distinct sources would define a new hybrid profile |
| Candidate or realization preference | No ranking accepted | No | If the proposal cannot remain symmetric and requires a design recommendation |
| Future-exhaustive A/C or five-realization roster | Blocked by the accepted successor rule | No | If the proposal claims completeness over all future GRC-v4 profiles |

**Current disposition:** Sections 8–10 are fillable from the accepted investigation without adding a candidate law, realization, root, writer, or theorem. They expose no scientific contradiction and no mandatory successor investigation. The strongest visible boundaries—A/C physical nonabsorbability, runtime endpoint effects, CI globality, RG2b differentiability, PC endpoint hysteresis, and profile ranking—remain exact claim ceilings rather than omissions in the substrate account.

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

> **Control lineage:** `D10-CL-N-001` through `D10-CL-N-009`; accepted D10.2 `claim_topology_effect` status update recorded under the non-node provenance label `D10_2_CL_N_001`; D10.2 parent and equation/contract registry.
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

This is the current status after D10.2. The accepted D10.2 audit's `claim_topology_effect` records the earlier conditional substrate-provenance question in `D10-CL-C-011` as succeeded under the provenance label `D10_2_CL_N_001`; the generic-substrate question must therefore not be presented as still unresolved for the current population. The label is not itself a queryable claim node, and the explorer correctly continues to expose the original D10 node with its historical `conditional` classification.

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

The accepted D10.2 promotion result is a specific record-level successor disposition for the older conditional substrate-identity question: the D10.2 audit names `D10_2_CL_N_001` in `claim_topology_effect`. It does not remove or relabel the historical `D10-CL-C-011` graph node. The current-population ceiling in `D10-CL-C-012` is not similarly changed and must remain visible.

The exploratory side tool can verify the `D10-CL-C-011` node, the accepted D10.2 audit-record identity, and their surrounding reconstructed provenance. It cannot query `D10_2_CL_N_001` as a claim or prove a graph successor edge, because neither was admitted as a graph node or edge. Verifying this particular status update therefore requires reading the two exact D10.2 `/claim_topology_effect` fields above. This bounded raw-record lookup is source-directed verification, not permission to infer missing graph structure. The tool may not decide that an unexecuted verification obligation has passed, fabricate a rerun result, or generate a new claim.

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

> **Associated accepted claims:** `D10-CL-N-001`; substrate-promotion predecessor `D10-CL-C-011`, whose accepted D10.2 record-level status update is carried by the non-node provenance label `D10_2_CL_N_001`.

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

GRC-v4 makes the historical part of the graph dynamics explicit without turning every historical influence into a new resource or one universal memory variable. The common substrate contract identifies causal roles and stage boundaries. A complete profile then supplies the particular retained representation, Read-Back map, current closure, write law, and temporal realization.

The central distinction is:

$$
\text{retention}
\neq
\text{Read-Back}
\neq
\text{write-back}.
$$

Retention says what remains causally available across beats. Read-Back says how that retained structure conditions present activity into an oriented current contribution. Write-back says how the consequences of the current beat change what will be available later. None of these terms is established merely by observing persistence, a slow coefficient, a diagnostic dependence, or an update performed outside the declared transition.

> **Provenance note:** Claim and parent-object associations below retain the explorer disposition `indeterminate_requires_review`. They are crosswalk references, not reconstructed proof or independent changes in claim status.

### 5.1 Role-level loop

At the architecture level, the accepted loop can be displayed as

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

Here $T_{M,k}$ names the **retained causal role** at beat $k$. It is not a claim that all profiles serialize an independent coordinate with that name. The role is realized differently by the admitted families:

| Profile contribution | Retained causal role | Authority status |
|---|---|---|
| Candidate A | positive retained edge mobility $W_{A,k}$ and its relation to the current instantaneous reference | $W_A$ is authoritative nonresource state |
| Candidate C | the selected $C$-sector and its induced Hodge response | only $C$ is authoritative; sector and Hodge surfaces are derived |
| PC and CI+PC | persistent structural carrier $Z_{4,a,k}$ in addition to the selected candidate state | $Z_{4,a}$ is realization-specific authoritative history |
| CI, OS, and RG2b without PC | no independent persistent $K_4$ carrier merely by realization name | geometry is solved, staged, or reconstructed according to the realization contract |

The direct current path and explicit Read-Back path must also remain distinct. Let $J_{0,a,k}$ denote the candidate/profile-specific baseline current evaluated with the explicit Read-Back gate disabled but with all direct retained-conditioned mobility or geometry effects preserved. Let $j_{a,k}$ denote the explicit Read-Back contribution. The common composition interface is

$$
J_{C,a,k}
=
J_{0,a,k}
+
\zeta_a j_{a,k}.
$$

This is a role equation, not a universal solved formula. Candidate A and Candidate C provide different Read-Back operators, different regular domains, and different current closures. CI and CI+PC may place the current inside a joint root; OS uses its frozen predictor–geometry–corrector sequence; RG2b reconstructs geometry; PC consumes persistent structural history. Section 10 supplies those realization-specific equations.

The decomposition has a fixed gauge. $J_0$ is defined independently of the explicit binary read gate $\chi_a$ and the physical coupling $\zeta_a$. Terms may not be moved between $J_0$ and $j$ after an outcome is observed. Otherwise “Read-Back on/off” would change the baseline class rather than isolate the explicit read channel.

Once solved, one $J_C$ is authoritative for continuity and every declared downstream consequence of that beat. A diagnostic read current, an intermediate trial current, a structural one-form, or a prior solver iterate cannot become a second resource current.

> **Primary source objects:** `L-AUTHORITATIVE-CURRENT`, `A-READ-CLOSURE`, `C-READ-BACK`.

> **Equation/contract rows:** `D10.2-EC-PARENT-L-AUTHORITATIVE-CURRENT`, `D10.2-EC-PARENT-A-READ-CLOSURE`, `D10.2-EC-C-RESOLVENT`, `D10.2-EC-C-READBACK`.

> **Associated accepted claims:** `D10-CL-N-003`, optional A/C claims `D10-CL-O-001` and `D10-CL-O-002`; physical nonabsorbability remains conditional under `D10-CL-C-007`.

### 5.2 Retention

Retention is defined through the complete causal state and its lawful transition, not by elapsed time alone. The accepted D2 terminology distinguishes:

- a **forming or write driver**, meaning a declared source current, input, or downstream state consequence admitted by the candidate writer;
- a **formed representation**, meaning a candidate representation that has left its neutral or instantaneously reconstructed baseline through a qualifying attributable write;
- **post-input retention**, meaning that formed content remains causally available after the forming or write driver is absent;
- **release**, meaning a declared return to neutral or declared removal of retained content with accounting and lifecycle provenance;
- **reconfiguration**, meaning a lawful change of retained content or address without automatically claiming new formation;
- **write**, meaning the declared transition from the beat-$k$ representation and admitted inputs to the beat-$(k+1)$ representation.

This gives retention an operational boundary. Initialization can construct or load a starting state, but does not establish native formation. Continuing external drive is not post-input retention. Administrative reset is not native release. A relation to a moving instantaneous reference may approach neutrality because the reference moved even when the authoritative retained state did not; that movement alone is not release evidence.

The common permitted mechanism classes include passive persistence, bounded decay, activity-maintained persistence after the external forming driver is absent, regeneration from another declared retained coordinate, transfer between declared retained representations, and metastable persistence. Each is lawful only when its maintaining inputs and state are inside the complete declared causal state.

A slow rate alone is not retention evidence. In particular, the following cannot secretly maintain a retained state:

- a lingering boundary input;
- a parameter schedule not returned to baseline;
- a scheduler flag or producer queue;
- a stale current or geometry cache;
- a mutable registry;
- repeated undeclared driver events;
- undeclared RNG-driven injection.

Every candidate has exactly one authoritative write per beat or an explicit no-write disposition. The write must state its inputs, temporal side, bounds, release semantics, state owner, and serializer/lifecycle consequences. Hidden pre-step or post-step writers are forbidden.

Candidate A realizes this requirement through one positive $W_A$ writer. Candidate C does not write an independent sector; its future retained-conditioned response changes because authoritative continuity changes $C$ and the sector/Hodge package is rederived. PC and CI+PC add one declared $Z_{4,a}$ writer. These are different retention mechanisms and must not be redescribed as one generic cache.

> **Primary source objects:** `A-RETAINED-WRITER`, `C-AUTHORITY`, `REAL-PC`.

> **Equation/contract rows:** `D10.2-EC-PARENT-A-RETAINED-WRITER`, `D10.2-EC-C-AUTHORITY`, `D10.2-EC-PC-WRITER-COEFFICIENT`, `D10.2-EC-PC-ZOH-WRITER`, `D10.2-EC-PC-RELEASE`.

> **Boundary:** formed-branch runtime preparation, post-input persistence, release, and replay remain unexecuted. The substrate defines lawful mechanisms and state transitions; it does not claim that a formed branch has been reached in runtime.

### 5.3 Read-Back

Read-Back is the profile-declared map by which retained causal structure conditions present activity into an oriented current contribution. Its input and output live on the current graph’s oriented edge space, or on explicitly identified one-form spaces with lawful flat/sharp maps. Its output is a derived current-like contribution, not an independently conserved stream and not a second resource reservoir.

The common operator contract requires:

- a declared domain and codomain;
- the current stage at which the operator is evaluated;
- the retained and geometric conditioning inputs;
- any nonretained read context;
- a passive zero-current null;
- covariance under graph relabeling and coordinate reorientation;
- candidate-specific parity under physical current reversal;
- fail-closed behavior outside the admitted domain.

Present activity is load-bearing. At fixed retained package, geometry, and read context, zero trial current produces zero Read-Back output. This operator-level null is not the same as zero baseline current, a full-loop equilibrium, energetic passivity, or absence of retained structure.

D5 evaluates the operator on an unsolved trial current. D6, or a later admitted realization, may substitute the unknown total current and solve the resulting closure. During that solve, all noncurrent read context declared at the pre-read stage remains frozen unless the complete profile explicitly admits a different recurrence. Recomputing the read context from the unknown current inside the same solve would change the realization and therefore the complete profile identity.

The explicit read-off control sets only the binary read gate $\chi_a$ to zero. It must preserve:

- the candidate’s retained state or derived retained package;
- the current geometry and topology;
- the baseline $J_0$ evaluation;
- the writer unless a separate write-off control is also applied.

This is what allows the explicit $j$ channel to be distinguished from direct retained-conditioned mobility or geometry effects already present in $J_0$.

Read-Back is directional because its output is an oriented edge quantity. That does not mean every retained representation stores historical chirality. Candidate A’s current retained content is scalar edge magnitude or unoriented-axis information; present current supplies the output orientation. Candidate C’s current selected scalar sector likewise does not by itself store chirality. Physical current reversal and coordinate reorientation therefore remain separate operations:

- **physical reversal** negates present flux at fixed coordinate orientation and fixed retained package;
- **coordinate reorientation** changes the stored edge basis and covariantly transforms incidence, metric, current, and output without changing physical state;
- **reversed forming history** requires rerunning or lawfully transforming the history and may not assume that a scalar carrier retains sign.

> **Primary source objects:** `A-READ-CLOSURE`, `C-READ-BACK`, `GEOM-COVARIANCE`.

> **Equation/contract rows:** `D10.2-EC-PARENT-A-READ-CLOSURE`, `D10.2-EC-C-RESOLVENT`, `D10.2-EC-C-READBACK`, `D10.2-EC-PARENT-GEOM-COVARIANCE`.

> **Boundary:** a typed operator family and a nonzero algebraic read response do not by themselves establish runtime reachability, physical-channel attribution, or nonabsorbability from a reparameterized baseline.

### 5.4 Authoritative total current

For every admitted profile, one solved current $J_C$ is authoritative. It is the current that enters the single continuity write and any other consequence explicitly assigned to current authority. The common interface is

$$
J_C
=
J_0+
\zeta j,
$$

but the solve is candidate- and realization-specific. The equation may reduce to an exact inverse on one regular profile, become a joint current/geometry root in CI, or be staged through predictor and corrector currents in OS. No common global uniqueness theorem is created by writing the same outer composition.

The current solve preserves three accounting rules.

First, $j$ is not an additional resource transfer. On a closed graph it enters the same internal current space and therefore the same incidence divergence as the rest of $J_C$. On an open graph, net transport must be represented by an explicit boundary ledger rather than attributed to an uncounted read stream.

Second, only the postsolve $J_C$ has current authority. A candidate writer may consume $J_C$ or a declared downstream consequence, but may not write directly from a diagnostic $j$ while bypassing the total-current closure. A structural source may consume the correctly lowered one-form associated with the read current, but that source is not the current used by continuity unless sharpened and admitted by the profile.

Third, branch and domain failure is fail-closed. Singular, multiple, nonfinite, or otherwise unadmitted roots do not authorize a fallback current, hidden regularization, or partial commit. A singular-current successor would be a new profile with its own derivation and failure semantics.

The separation among current surfaces is therefore:

| Surface | Role | Authority |
|---|---|---|
| $J_0$ | direct baseline current with explicit read gate off | derived profile surface |
| $J_{\mathrm{trial}}$ | input to the Read-Back operator before closure | transient solver surface |
| $j$ | explicit retained-conditioned read contribution | derived current-like surface |
| $j_{\mathrm{struct}}^\flat$ | lowered one-form used by structural $K_4$ construction | derived structural surface |
| $J_C$ | solved physical current for continuity and declared consequences | authoritative same-beat current |

> **Primary source object:** `L-AUTHORITATIVE-CURRENT`.

> **Associated accepted claim:** `D10-CL-N-003`.

> **Bounded overread:** complete-chain consumption does not by itself establish a nonzero committed endpoint effect; that stronger proposition remains under `D10-CL-C-004` and `D10-CL-U-002`.

### 5.5 Write-back

Write-back is the accepted profile-specific transition by which the present beat changes the causal structure available to a later beat. Its meaning depends on the authority class of the profile.

The common write-input contract distinguishes three temporal classes:

```text
pre-solve:
    retained state at k
    C_k
    declared incoming or preclosure current surfaces
    geometry, topology, lifecycle, and clock at k

post-solve:
    J_C,k only after the total-current closure has been solved

post-state-update:
    C_{k+1}
    another declared downstream consequence at k+1
```

A writer may use only the temporal classes explicitly admitted by its profile. If $J_C$ depends on the new candidate state at $k+1$, the transition contains an implicit cycle and must be represented by a realization that actually solves that cycle. A nominally explicit writer cannot read its own new output in the same beat.

The admitted write-back classes are distinct:

1. **Direct retained-state write.** Candidate A writes the authoritative positive edge state $W_A^{k+1}$ once, after evaluating its accepted post-continuity target from $C_{k+1}$, solved $J_C$, and refreshed differentials.
2. **Resource-mediated future rederivation.** Candidate C commits only $C_{k+1}$. Its selected sector, Hodge package, resolvent, and later Read-Back are rederived from that authoritative state. No independent $T_C$ write exists.
3. **Realization-history write.** PC and CI+PC update the independently authoritative structural carrier $Z_{4,a,k+1}$ according to their declared ZOH law.
4. **Lifecycle write.** Reset, migration, release, archive, or topology transport may transform or discard retained content only through the typed lifecycle contract and its receipts.

If several forming contributions arrive in one beat, they enter one declared write batch. Their composition must be a declared commutative bounded sum, a deterministically ordered composition with serialized order, a declared competition/normalization rule, or a deterministic priority rule. Undefined iteration order and external producer sequence memory are forbidden.

Formation, retention, reconfiguration, and release may be causal attributions of one writer rather than separate additive writers. In particular, release need not be the algebraic inverse of formation, but it must be native, bounded, attributable, and lifecycle-recorded. Administrative reset cannot be relabeled as release.

> **Primary source objects:** `A-WRITER-TARGET`, `A-RETAINED-WRITER`, `C-AUTHORITY`, `REAL-PC`, `L-POSTCONTINUITY-REFRESH`.

> **Equation/contract rows:** corresponding D10.2 parent rows plus `D10.2-EC-PC-ZOH-WRITER` and `D10.2-EC-PC-RELEASE`.

### 5.6 Passive and null surfaces

The investigation deliberately separated controls that are often conflated under “turn memory off.” The following table is part of the substrate content because each intervention preserves a different causal remainder.

| Surface or control | Operation | What remains active | What it does not establish |
|---|---|---|---|
| Initialization | construct or load a declared start state | ordinary profile dynamics | native formation |
| No forming or write input | remove only the external/activity forming driver | ordinary writer and runtime evolution | write-off or frozen state |
| Zero present current | set trial/current input to zero at fixed retained package | retained state and geometry | no retained content or full equilibrium |
| Read off | set only $\chi_a=0$ | direct $J_0$ path, retained state, writer | carrier neutralization or write-off |
| Gain off | set the physical coupling $\zeta_a=0$ | diagnostic read surface may remain | read operator absence |
| Write off | disable the constitutive retained/history write | current read may remain active | frozen complete dynamics |
| Frozen carrier | hold the lawful retained package fixed for a read probe | current and read enactment | a lawful independent runtime intervention for a derived Candidate C sector |
| Carrier neutral | replace the retained relation/package by its preregistered neutral reference | read gate and present current | read-off |
| Administrative reset | restore the declared reset baseline | post-reset profile dynamics | native release |
| Failed solve | reject the beat and commit nothing | prestate only | a passive valid transition |
| Disabled V4 profile | apply the exact profile-scoped transition, state, observable, and lifecycle reduction | GRC9V3 target behavior in the specialization | generic read-off, write-off, or proof of future profile equivalence |

For Candidate C, an independent runtime switch of $T_C$ at fixed $C$ is unlawful because $T_C$ is derived. A fixed-$T_C$ comparison may be used only as an explicitly labelled algebraic operator probe, or replaced by a reachable matched-$C$ comparison. The distinction between literal runtime interventions, on-manifold matched counterfactuals, and off-manifold algebraic probes must remain visible.

The passive zero-current null is operator-level only. It does not require $J_0=0$, does not claim energetic passivity, and does not say that retained structure has no direct effect through mobility or geometry.

### 5.7 Causal-loop claim ceiling

The accepted investigation establishes a closed **design-level causal architecture** for the current admitted profiles:

```text
declared retained role and authority
-> typed Read-Back contribution
-> candidate/realization-specific total-current closure
-> one authoritative continuity write
-> declared candidate and/or history writer
-> later retained role
```

This closure is Markovian on each complete declared state, stage-ordered, resource-accounted, and fail-closed. It is strong enough to define the substrate and its admissible profiles.

It does not establish:

- runtime-reached native formation;
- post-input persistence over a measured horizon;
- native release or replay in an implementation;
- a nonzero committed endpoint effect;
- endpoint hysteresis;
- physical nonabsorbability of A or C;
- physical-channel attribution;
- temporal or structural stability;
- a continuation spectrum;
- one universal retained object or one universal current solver.

These are accepted boundaries rather than contradictions in the common causal architecture. Section 5 therefore requires no successor investigation. A successor would be required only if the final substrate account attempted to make one of the stronger claims rather than preserving it as outside the current result.

---

## 6. Structural Geometry, Hodge Typing, and Mobility

GRC-v4 separates the structural object generated by activity from the geometry that realizes it and from the mobility that transports resource. This separation is essential: the same edge dimension and even the same diagonal reference numbers can represent different mathematical types and different causal authority.

The accepted chain is

$$
K_4
\longrightarrow
H_4
\longrightarrow
h_4,
$$

with an explicit profile map, positive-domain contract, and realization-specific causal consumer. It is not a relabeling of the GRC9V3 cached node tensor, and it does not authorize geometry to take over candidate mobility.

### 6.1 Core structural role and graph $K_4$

Core Reflexive Coherence supplies the substrate-independent constitutive role

$$
K
\longrightarrow
g[K].
$$

It does not uniquely determine a graph matrix, an overlap normalization, a Hodge star, or a temporal realization. GRC-v4 realizes that role on the finite oriented graph through a graph-local symmetric bilinear object $K_4$ acting on the oriented one-form space $\Omega^1(\mathcal G)$.

The complete structural input is separated into a declared baseline and an activity-dependent increment:

$$
K_4
=
K_{4,\mathrm{base}}
+
\Delta K_4.
$$

A profile must say explicitly whether it consumes the total $K_4$ or the increment $\Delta K_4$. The current common assembly constructs the increment from stable vertex-star restrictions of the correctly lowered structural current.

For each live vertex $v$, let $R_v$ restrict a global oriented edge one-form to the edges in the declared vertex star. Let $m_e$ be the number of declared stars containing edge $e$, and define the local diagonal partition weight by

$$
(D_v)_{ee}
=
m_e^{-1/2}.
$$

For a structural one-form $j^\flat$, define

$$
j_v
=
D_vR_vj^\flat.
$$

The accepted partition identity is

$$
\sum_v
R_v^\top D_v^2R_v
=
I
$$

on the live oriented edge space. The common star assembly is

$$
\mathcal A_\star(j^\flat)
=
\sum_v
R_v^\top
\bigl(j_vj_v^\top\bigr)
R_v.
$$

The candidate-specific typed adapter and gain then produce

$$
\Delta K_{4,a}
=
\iota_a\!\left(
\mathcal A_\star(j_{a,\mathrm{struct}}^\flat)
\right).
$$

The adapter $\iota_a$ preserves the already accepted candidate-specific payload type, units, and scaling. The common assembly does not introduce a new universal $K_4$ gain or borrow one candidate’s structural source for another candidate.

The assembled increment is symmetric positive semidefinite for the accepted rank-one subprofile, finite-radius graph-local, covariant under graph relabeling and signed edge reorientation, and zero at zero structural current. The partition identity removes unrecorded diagonal edge multiplicity. It does not make every off-diagonal pair weight unique: the factor determined by how often an edge pair co-occurs in the selected cover remains a bounded cover-dependent choice.

Graph-local assembly is also not the same as local causal support. A candidate Read-Back operator may be nonlocal on a connected component, and a sparse Hodge matrix need not have a sparse inverse. Locality of the assembly therefore cannot be used to claim a local total response.

> **Primary source objects:** `CORE-K-STRUCTURAL-ROLE`, `GEOM-K4`, `GEOM-ASSEMBLY`.

> **Equation/contract rows:** `D10.2-EC-PARENT-CORE-K-STRUCTURAL-ROLE`, `D10.2-EC-PARENT-GEOM-K4`, `D10.2-EC-PARENT-GEOM-ASSEMBLY`, `D10.2-EC-GEOM-K4-ASSEMBLY`.

> **Associated accepted claim:** `D10-CL-N-006`; classical structural-Hessian and alpha claims remain conditional under `D10-CL-C-001`, while alternative normalization remains open under `D10-CL-U-005`.

### 6.2 Reference Hodge embedding and typed current spaces

The current accepted reference profile embeds graph measure and positive GRC baseline conductance into distinct Hodge and current-metric objects. On a fixed graph stratum,

$$
H_{0,\mathrm{ref}}
=
\operatorname{diag}(\mu),
$$

$$
H_{1,\mathrm{form,ref}}
=
\operatorname{diag}(W_{\mathrm{ref}}),
$$

and

$$
G_{J,\mathrm{ref}}
=
\operatorname{diag}(W_{\mathrm{ref}}^{-1}).
$$

These expressions do not give the three objects the same type.

- $H_0$ is the zero-form measure/Gram operator on vertex fields.
- $H_{1,\mathrm{form}}$ is the structural one-form Hodge or Gram operator used for one-form inner products, graph-Hodge operators, and structural geometry.
- $G_J$ is the resistance/current metric and the flat map from physical oriented edge flux coordinates to structural one-form coordinates.

The reference relation

$$
G_{J,\mathrm{ref}}
=
H_{1,\mathrm{form,ref}}^{-1}
$$

belongs to the selected paired graph-Hodge realization. It is not a license to use the same symbol for both objects.

For a physical flux $j_{\mathrm{flux}}$, the structural one-form is

$$
j_{\mathrm{struct}}^\flat
=
G_J(h)
\,j_{\mathrm{flux}}.
$$

Conversely, the physical flux associated with an admitted structural one-form is obtained by the corresponding sharp map,

$$
j_{\mathrm{flux}}
=
G_J(h)^{-1}
\,j_{\mathrm{struct}}^\flat.
$$

Continuity and current accounting consume physical flux. The rank-one $K_4$ structural source consumes $j_{\mathrm{struct}}^\flat$. Equal vector lengths do not allow the physical flux array to be used directly as a lowered one-form.

The current reference package may be written as

$$
h_{4,\mathrm{ref}}
=
\bigl(
H_{0,\mathrm{ref}},
H_{1,\mathrm{form,ref}},
B_{\mathrm{ref}},
\partial_{\mathrm{ref}}
\bigr),
$$

where graph incidence, boundary convention, and the live node/edge order are fixed on the current stratum. This is a V4 reference embedding constructed from admitted GRC surfaces. It is not a claim that GRC-v3 already possessed the full V4 generated geometry or anisotropic transport.

> **Primary source objects:** `GEOM-H1-FORM`, `GEOM-GJ`.

> **Equation/contract rows:** `D10.2-EC-PARENT-GEOM-H1-FORM`, `D10.2-EC-PARENT-GEOM-GJ`, `D10.2-EC-GEOM-FLAT`.

> **Type-control source:** accepted `D7GPostv2GraphHodgeTypeCorrection`.

### 6.3 Structural crossing and geometry profile

A named geometry profile maps the graph-local structural increment, the reference geometry, and explicit profile context into the admitted positive graph-Hodge class. The profile law is not itself a geometry state, and the geometry state is not itself a transport mobility operator.

For the accepted affine reference-relative profile, define the dimensionless increment

$$
\Theta_4
=
\kappa_H
H_{1,\mathrm{form,ref}}^{-1/2}
\Delta K_4
H_{1,\mathrm{form,ref}}^{-1/2}.
$$

The admitted domain requires

$$
I+\Theta_4
\succ
0.
$$

On that domain, the one-form Hodge update is

$$
H_{1,\mathrm{form}}^+
=
H_{1,\mathrm{form,ref}}^{1/2}
(I+\Theta_4)
H_{1,\mathrm{form,ref}}^{1/2}
=
H_{1,\mathrm{form,ref}}
+
\kappa_H\Delta K_4,
$$

while the current initial profile keeps the zero-form measure fixed:

$$
H_0^+
=
H_{0,\mathrm{ref}}.
$$

The resulting geometry package is

$$
h_4^+
=
\bigl(
H_0^+,
H_{1,\mathrm{form}}^+,
B_{\mathrm{ref}},
\partial_{\mathrm{ref}}
\bigr).
$$

For the selected paired realization,

$$
G_J(h_4^+)
=
\bigl(H_{1,\mathrm{form}}^+\bigr)^{-1}.
$$

The neutral reduction is exact: $\Delta K_4=0$ or $\kappa_H=0$ returns the supplied reference package. For nonzero $\kappa_H$, a nonzero admitted $\Delta K_4$ produces a nonzero one-form Hodge change; the crossing does not erase off-diagonal structure through scalar projection.

The common substrate fixes this typed map and its domain. The selected geometry-temporal realization fixes when the geometry is constructed, whether it participates in a simultaneous root, whether it is consumed in an operator-split correction, whether it is reconstructed, and whether persistent structural history contributes. Thus

$$
K_4
\longrightarrow
H_4
\longrightarrow
h_4
$$

is load-bearing only through a declared current/transition consumer. Producing $h_4$ as an unconsumed diagnostic or cache is not structural Read-Back and does not close a causal loop.

> **Direct parent objects:** `GEOM-H1-FORM`, `GEOM-GJ`, `GEOM-K4-TO-H4-TO-h4`.

> **Equation/contract rows:** `D10.2-EC-GEOM-HODGE-UPDATE`, `D10.2-EC-GEOM-PROFILE`, `D10.2-EC-GEOM-FLAT`.

> **Boundary:** the affine graph-Hodge law is the accepted current reference profile, not the unique core-theory $g[K]$, not a canonical continuum metric theorem, and not a future-exhaustive geometry family.

### 6.4 Transport mobility remains separate

The transport mobility operator $M_4$ acts on the physical current transport space and is owned by the selected candidate factorization. It is distinct from the structural Hodge package even where a legacy reference produces the same diagonal numbers.

The type boundary is

$$
M_4
\neq
H_{1,\mathrm{form}}
\neq
G_J
\neq
h_4
\neq
\mathcal A_\star(j^\flat).
$$

These inequalities express different mathematical and causal roles, not merely unequal numerical arrays.

- $M_4$ determines transport response in the current solve.
- $H_{1,\mathrm{form}}$ supplies the structural one-form geometry.
- $G_J$ lowers physical flux to a one-form and measures current/flux resistance.
- $h_4$ is the graph-Hodge geometry package.
- $\mathcal A_\star$ assembles a structural bilinear increment.

For Candidate A, the accepted transport factorization is

$$
M_{4,A}
=
\eta\,
\operatorname{diag}(W_A).
$$

This preserves $W_A$ as mobility authority. Candidate C retains its accepted candidate-specific baseline and identification factorization; its mobility must be copied from the accepted Candidate C source rather than inferred from $H_{1,\mathrm{form}}$, $G_J$, or a coincident matrix shape.

No map

```text
H1_form -> M4
G_J     -> M4
h4      -> M4
```

exists in the current common contract. A future profile may relate geometry and mobility only by introducing an explicit constitutive map, new profile identity, provenance, units, staging, and the required contract reopening.

The positive scalar baseline mobility $W$ introduced in §4.1 is likewise not automatically the full V4 transport operator of every profile. It supplies the inherited scalar potential-flow reference. Candidate A promotes a positive retained edge field into its declared mobility authority; other candidates own their transport factorization separately.

> **Primary source object:** `GEOM-M4`.

> **Equation/contract rows:** `D10.2-EC-PARENT-GEOM-M4`, `D10.2-EC-GEOM-MOBILITY-BOUNDARY`.
>
> **Derivation source:** `D10.2-DER-MOBILITY`.

> **Associated accepted claim:** `D10-CL-N-006`.

### 6.5 Covariance and support

The common geometry construction is covariant under graph relabeling and signed edge-coordinate reorientation. Let $U$ be the signed edge permutation induced by a stable graph isomorphism and orientation change. Then the structural and Hodge objects transform by congruence:

$$
\Delta K_4'
=
U\Delta K_4U^\top,
$$

$$
H_{1,\mathrm{form}}'
=
UH_{1,\mathrm{form}}U^\top,
$$

and physical and structural currents transform in their corresponding edge coordinates:

$$
j_{\mathrm{flux}}'
=
Uj_{\mathrm{flux}},
\qquad
j_{\mathrm{struct}}^{\flat\prime}
=
Uj_{\mathrm{struct}}^\flat.
$$

The profile map, flat/sharp identification, and current consumer must commute with the same typed transport. A coordinate sign change therefore does not create a physical history reversal. It changes the representation of the same oriented object.

The fixed-stratum covariance contract does not define topology-event transport. When the node or edge space changes dimension, $H_0$, $H_{1,\mathrm{form}}$, $G_J$, $K_4$, candidate state, current, and history require typed interspace maps, reconstruction, or explicit loss. Those event contracts belong to Section 12.

The common construction also separates three support notions:

1. **assembly support:** which graph restrictions enter the local star sum;
2. **operator support:** which entries of a Hodge, response, or inverse operator may be nonzero;
3. **causal support:** which parts of the graph can affect an output after the full candidate and realization chain.

A graph-local $K_4$ assembly does not make a nonlocal resolvent local, and a sparse one-form Hodge does not imply a sparse inverse or solver influence.

> **Primary source object:** `GEOM-COVARIANCE`.

> **Equation/contract row:** `D10.2-EC-PARENT-GEOM-COVARIANCE`.

> **Boundary:** form-level covariance is accepted; executable general-SPD conditioning, inverse-solver behavior, and runtime covariance remain verification obligations under `D10-CL-C-006`.

### 6.6 Geometry claim ceiling

Section 6 establishes the current bounded graph-generic geometry content:

- the distinction between core $K\mapsto g[K]$ and graph $K_4$;
- a common graph-local symmetric bilinear $K_4$ domain;
- overlap-normalized vertex-star assembly;
- correct lowering from physical flux to structural one-form;
- the explicit reference embedding $H_{0,\mathrm{ref}}$, $H_{1,\mathrm{form,ref}}$, and $G_{J,\mathrm{ref}}$;
- the accepted affine positive Hodge update;
- the load-bearing $K_4\to H_4\to h_4$ profile interface;
- candidate-specific transport-mobility authority;
- graph-relabeling and signed-edge covariance.

It does not establish:

- that the accepted star-pair normalization is unique;
- that the simple reference star pair is the only lawful DEC realization;
- a continuum-limit uniqueness theorem;
- one universal relation between geometry and transport;
- common physical units or equal structural capacity across A and C;
- executable general-SPD conditioning and inverse-solver guarantees;
- topology transport from fixed-stratum congruence alone;
- structural marginality, temporal stability, or a continuation spectrum;
- a unique geometry-temporal realization.

These limits are already represented by the accepted claim topology. No successor investigation is required to state the common geometry. A successor becomes necessary only if the intended proposal attempts to cross one of these boundaries—for example by asserting a unique Hodge normalization, universal geometry-to-mobility map, or cross-profile quantitative comparison.

---

## 7. Complete Profile Grammar

The common GRC-v4 substrate is executable only through a **complete profile identity**. The profile grammar prevents a candidate equation, geometry law, temporal realization, solver, or lifecycle convention from being changed while the state continues to carry the same scientific label.

The selected architecture is therefore:

$$
\boxed{
\text{common GRC-v4 contract}
+
\text{one constitutive family}
+
\text{one geometry-temporal realization}
+
\text{complete profile-local contract}
}.
$$

This is a specification-meta structure grounded in the investigation. It does not add causal state and does not rank the admitted profiles.

### 7.1 Two independent profile axes

The current admitted constitutive families are

$$
\mathcal A_{\mathrm{constitutive}}
=
\{\mathrm A,\mathrm C\},
$$

and the current admitted geometry-temporal realizations are

$$
\mathcal R_{\mathrm{temporal}}
=
\{\mathrm{CI},\mathrm{OS},\mathrm{RG2b},\mathrm{PC},\mathrm{CI+PC}\}.
$$

Their current initial product is

$$
\mathcal P_{\mathrm{initial}}
=
\mathcal A_{\mathrm{constitutive}}
\times
\mathcal R_{\mathrm{temporal}}.
$$

It contains ten complete profile identities:

| Constitutive family | CI | OS | RG2b | PC | CI+PC |
|---|---|---|---|---|---|
| A | `A_CI` | `A_OS` | `A_RG2b` | `A_PC` | `A_CI_PC` |
| C | `C_CI` | `C_OS` | `C_RG2b` | `C_PC` | `C_CI_PC` |

Every executable runtime state binds exactly one constitutive family and exactly one realization. Zero candidates, zero realizations, ambiguous unions, and same-state mixtures are not admissible executable identities.

The current state, reset state, and each scientific snapshot bind one complete profile identity. Profile-migration receipts bind the ordered pair

$$
(p_{\mathrm{source}},p_{\mathrm{target}}),
$$

and topology-event receipts bind the corresponding ordered source and target profiles, with equality only when the complete profile is unchanged.

An implementation may support any nonempty subset of the ten admitted profiles. It may not claim conformance to a profile whose complete equations, state, solver, lifecycle, and reductions it does not implement.

The current population is complete for the **initial lineage-local specification population**. It is not a theorem that every lawful future GRC-v4 profile belongs to this product.

> **Primary source objects:** `L-PROFILE-GRAMMAR`, `SPEC-PROFILE-GRAMMAR`.

> **Equation/contract rows:** `D10.2-EC-PARENT-L-PROFILE-GRAMMAR`, `D10.2-EC-PARENT-SPEC-PROFILE-GRAMMAR`.

> **Associated accepted claims:** `D10-CL-N-009`; lifecycle binding `D10-CL-N-005`; future-exhaustiveness boundary `D10-CL-C-012`.

### 7.2 Profile-local contract

A shorthand such as

$$
p
=
(a,r,\Theta_p)
$$

may be used only if $\Theta_p$ denotes the entire identity-bearing contract rather than an editable bag of numerical parameters. A complete profile must declare the following surfaces.

| Contract group | Required contents |
|---|---|
| Identity | constitutive family, realization family, profile ID, predecessor/provenance |
| State authority | resource state, authoritative nonresource state, realization history, reset state |
| Derived surfaces | differential backend, selectors, Hodge objects, Read-Back surfaces, geometry |
| Current | $J_0$ definition, Read-Back map, coupling gains, authoritative closure, current space |
| Structural geometry | $K_4$ source, assembly, adapter, geometry profile, mobility factorization, consumer |
| Timing | exact stage order, pre-read context, solver substages, post-continuity refresh, writer order |
| Numerical/type contract | units, gauge, normalization, parameter domain, positivity/coercivity bounds |
| Solver | equation/root problem, branch rule, tolerances if normative, singular and multiple-root disposition |
| History | formation, retention, release, reconfiguration, capacity, ZOH or other writer where present |
| Lifecycle | snapshot, reset, migration, event transport/reconstruction, receipts, serializer identity |
| Compatibility | disabled transition, state, observable, and lifecycle reductions |
| Evidence ceiling | supported claims, conditional claims, open questions, negative relabels, verification obligations |

Normalization, units, gauge, domain, solver, and composition law are not implementation decoration. They are part of profile identity whenever they change the mathematical map, admitted state, branch, or comparison class.

Likewise, the composition coefficients of CI+PC are identity-bearing. The current accepted gain-two profile cannot be changed to another immediate/retained weighting while retaining the same profile ID. A materially different composition requires a successor.

The profile contract also preserves candidate neutrality. A and C satisfy the same common evidentiary burden, but do not need identical state or equations. CI, OS, RG2b, PC, and CI+PC likewise satisfy common completeness requirements while retaining distinct timing and history semantics.

> **Primary source objects:** `SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER`, `SPEC-COMPOSITION-PROFILE-IDENTITY`.

> **Equation/contract rows:** corresponding D10.2 parent rows.

> **Associated accepted claim:** `D10-CL-N-008`.

### 7.3 Successor admission and earliest-contract reopening

A materially distinct successor may not enter by silently modifying an admitted profile. The accepted admission rule requires:

1. explicit provenance or a new derivation;
2. a new complete profile identity;
3. identification of the earliest accepted contract whose semantics change;
4. reopening of every downstream claim or artifact reached through that contract;
5. preservation or explicit transformation of negative and conditional boundaries;
6. renewed substrate-provenance classification where the new profile could alter the GRC-v4/GRC9V4 factorization.

The earliest contract is determined by the substance of the change, not by where it is easiest to patch a document. A successor must reopen the earliest affected axis among:

```text
authority
staging
state
geometry
accounting
lifecycle
```

Examples include:

- a curvature-conditioned Candidate A law reopening the Candidate A constitutive functional and profile identity;
- an independent Candidate C sector state reopening state authority rather than merely the selector formula;
- a new persistent carrier law reopening realization-history authority and lifecycle;
- a different CI+PC gain reopening composition identity;
- an $h_4\to M_4$ constitutive map reopening geometry/mobility authority;
- a new topology-history transport reopening lifecycle and event accounting;
- a singular-current continuation reopening domain, solver, branch, and failure semantics.

The claim topology does not prescribe a fixed D11, D12, or later schedule. Conditional and open claims activate only when their stronger proposition or successor direction is attempted. Verification obligations gate only the claims they name; they are not a mandatory linear backlog.

For the proposal process, this means that a new investigation item should arise from an exact paper-exposed boundary, not from the mere existence of another mathematically possible profile. The content draft may reorganize accepted results, but may not fill the boundary itself.

> **Primary source object:** `SPEC-FUTURE-ADMISSION`.

> **Equation/contract row:** `D10.2-EC-PARENT-SPEC-FUTURE-ADMISSION`.

> **Current promotion status:** The accepted D10.2 audit records the bounded promotion for the current D10 initial population under the non-node provenance label `D10_2_CL_N_001`. Every materially distinct future profile reopens provenance and the earliest affected contract.

### 7.4 Candidate B remains a reserved extension slot

Candidate B is routed, not rejected. It remains a named successor possibility for an independent derived carrier, but no executable B profile is currently admitted.

B lacks a source-backed complete writer that fixes:

- the authoritative carrier type and state;
- formation inputs and attribution;
- post-input retention;
- native release and reconfiguration;
- bounded capacity and normalization;
- Read-Back typing;
- geometry and mobility relations;
- complete-step staging;
- reset, migration, event, and serialization behavior.

Without that package, B cannot be made executable by assigning it a placeholder array or borrowing another profile’s writer.

The persistent carrier realization PC is not Candidate B. PC supplies a particular scalar-ZOH, one-$\tau_{\mathrm{PC}}$ structural-history law that composes with Candidate A or Candidate C. Relabeling PC as B would collapse the constitutive axis into the realization axis and erase the exact state and writer question that keeps B open.

Similarly, neither A nor C may be renamed B because one of their derived surfaces resembles a carrier. A has authoritative retained mobility; C has a sector derived from authoritative $C$. B would require its own source-backed ontology and transition.

> **Primary source object:** `SPEC-B-SLOT`.

> **Equation/contract row:** `D10.2-EC-PARENT-SPEC-B-SLOT`.

> **Claim relations:** open `D10-CL-U-001`; negative boundary `D10-CL-X-005` blocks PC-as-B relabeling.

### 7.5 Claim ceilings and verification remain meta-contracts

Every complete profile carries a claim ceiling, but the claim registry is not part of the physical causal state. It records what the investigation supports, what stronger statements remain conditional, what questions remain open, and which relabels are currently false.

The profile-local claim contract prevents several common shifts:

- an optional admitted profile becoming a preferred profile without matched evidence;
- a conditional result becoming normative because the equation is present;
- an unexecuted verification obligation becoming unresolved constitutive mathematics;
- a negative boundary disappearing when a successor is discussed;
- a bounded reference profile becoming a universal theorem;
- a design-level transition becoming an implementation claim;
- a current-population roster becoming a future-exhaustive taxonomy.

`SPEC-VERIFICATION-REGISTRY`, already extracted in §2.5, remains active here. Runtime, numerical, and implementation obligations are separate from the scientific claim topology. Their separation works in both directions:

- lack of runtime verification does not automatically reopen an accepted design equation;
- acceptance of a design equation does not satisfy runtime, stability, attribution, or serializer conformance.

The claim topology is therefore an evolving scientific dependency graph rather than a checklist attached to the runtime. A new claim transforms named edges and debts through evidence; it does not silently alter the substrate state or schedule every open possibility for execution.

> **Primary source objects:** `SPEC-CLAIM-CEILINGS`, `SPEC-VERIFICATION-REGISTRY`.

> **Equation/contract rows:** corresponding D10.2 parent rows.

> **Control boundary:** claim governance is not runtime causal state, and verification obligations gate named claims rather than a mandatory successor sequence.

### 7.6 Complete-profile grammar claim ceiling

Section 7 establishes:

- exactly one admitted constitutive family and one admitted realization per executable state;
- ten complete current profile identities;
- identity binding for current state, reset state, snapshots, migration receipts, and topology-event receipts;
- profile-local declaration of authority, equations, stages, units, gauge, normalization, domain, solver, history, lifecycle, and compatibility;
- successor admission through new identity, provenance, and earliest-contract reopening;
- Candidate B as routed, unrejected, and nonexecutable;
- claim ceilings and verification registries as specification-meta contracts.

It does not establish:

- that the ten profiles exhaust GRC-v4;
- that every implementation must support all ten profiles;
- that one candidate or realization is preferred;
- that the current constants or normalizations are universal;
- that PC is the universal persistent-carrier law;
- that Candidate B is impossible or already supplied;
- a fixed successor schedule;
- implementation conformance.

No successor investigation is required by the profile grammar itself. The grammar instead defines how a later paper-exposed boundary becomes a lawful successor investigation rather than an untracked amendment.

---

## 8. Constitutive Family A: Retained Edge Mobility

Candidate A is the admitted revision-specific family in which positive edge mobility is an authoritative nonresource state, is read relative to a current instantaneous reference, modifies the authoritative physical current, and is written across beats by a positive multiplicative law. The family supplies a complete candidate-local recurrence. Geometry-temporal realizations determine when and how the accepted structural geometry is consumed.

A is not inherited core, is not the unique GRC-v4 completion, and is not selected over Candidate C. The accepted current profile is normalized and nondimensional. Its physical dimensionalization, explicit-channel nonabsorbability, runtime formation and release, and committed endpoint effects remain outside the present claim.

> **Provenance note:** The typed forensic audit reconstructed every cited claim, queried every cited parent through `object_dependents`, and queried every cited equation/contract row through `contract_provenance`. The contract associations retain `indeterminate_requires_review`; they are source crosswalks, not independently reconstructed proof.

### 8.1 Authoritative state and derived surfaces

For an A profile without a realization-specific persistent carrier, the independent candidate coordinates are

$$
X_{A,k}
=
\bigl(C_k,W_{A,k}\bigr),
$$

together with graph, context, complete-profile identity, reset state, charge target, and declared lifecycle parameters. The edge field satisfies

$$
W_{A,k,e}>0.
$$

Here $C_k$ is the sole resource coordinate and $W_{A,k}$ is authoritative retained mobility. The following are derived or same-beat surfaces rather than additional candidate state:

- graph differential summaries;
- the A potential $\Phi_A$;
- baseline current $J_{0,A}$;
- instantaneous reference $\widehat W_A$;
- directional contrast $q_A$;
- explicit read current $j_A$;
- authoritative total current $J_{C,A}$;
- structural one-form $j_A^\flat$;
- structural source $\Delta K_{4,A}$;
- post-continuity writer target $W_{\mathrm{drv},A}$.

A realization with persistent carrier state adds its own $Z_{4,A}$ coordinate through the complete-profile contract; it does not change the authority of $W_A$.

A cached potential, reference mobility, current, contrast, geometry, or writer target may be serialized for exact restoration only under the declared lifecycle format. Serialization does not give it independent causal authority. Rebuilding the accepted surface from authoritative state and context must reproduce the same transition.

> **Primary source object:** `A-STATE-REDUCTION`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-STATE-REDUCTION`.

> **Associated accepted claim:** Candidate A is an optional admitted profile under `D10-CL-O-001`; it is not inherited core and cannot be relabeled as such.

### 8.2 Baseline transport with A mobility authority

At the accepted reference geometry, Candidate A reuses the inherited graph potential and potential-flow forms with $W_A$ as the positive scalar mobility authority:

$$
\Phi_{A,i}^{D7}
=
\kappa_c
\sum_{e\sim i}
W_{A,e}
\bigl(C_i-C_{\operatorname{nbr}(e,i)}\bigr)
-
V_{\mathrm{site}}'(C_i),
$$

and, for the chosen edge orientation $e=(u,v)$,

$$
J_{0,A,e}^{D7}
=
-\eta W_{A,e}
\bigl(\Phi_{A,u}^{D7}-\Phi_{A,v}^{D7}\bigr).
$$

Equivalently, on the accepted typed spaces,

$$
M_{4,A}(W_A)
=
\eta\,\operatorname{Diag}(W_A),
$$

$$
J_{0,A}^{D7}
=
-M_{4,A}(W_A)\,d_0\Phi_A^{D7}.
$$

This baseline already depends on retained $W_A$. Disabling the explicit Read-Back gate therefore does not remove every historical effect. It removes the explicit relation-conditioned read channel while preserving the direct retained-mobility path. That separation is required for every A control and attribution claim.

When a realization supplies an admitted nonreference geometry $h$, the accepted geometry consumer is reference-relative:

$$
\Delta_0(h)
=
H_{0,\mathrm{ref}}^{-1}
B
H_{1,\mathrm{form}}(h)
B^\top,
$$

$$
\Phi_A(C,W_A,h)
=
\Phi_A^{D7}(C,W_A)
+
\kappa_{Ah}
\bigl[
\Delta_0(h)-\Delta_0(h_{\mathrm{ref}})
\bigr]C,
$$

$$
J_{0,A}(C,W_A,h)
=
-M_{4,A}(W_A)\,d_0\Phi_A(C,W_A,h).
$$

At $h=h_{\mathrm{ref}}$, the additional term vanishes exactly and the accepted D7 baseline is recovered. The coefficient $\kappa_{Ah}$ is profile-local, typed, and revision-specific. Its accepted enabled value and sign are profile choices, not theory-fixed constants or optimized stability parameters.

This geometry consumer does not define a generic $h\mapsto W_A$ writer. $W_A$ remains the mobility owner; geometry changes the potential used by the current solve. Any direct geometry-to-mobility authority transfer would be a materially distinct successor profile.

> **Primary source objects:** `BASE-SCALAR-MOBILITY`, `GEOM-M4`, `REAL-CI`, `REAL-OS`.

> **Equation/contract rows:** corresponding parent rows, `D10.2-EC-CI-A-ROOT`, `D10.2-EC-OS-A-CORRECTOR`.

> **Associated accepted claims:** `D10-CL-N-001`, `D10-CL-N-006`, `D10-CL-O-003`, `D10-CL-O-004`.

### 8.3 Accepted conductance functional

The accepted current A profile uses the curvature-disabled conductance functional

$$
G_{W,e}(C,J)
=
\max\!\left(
W_{\mathrm{floor}},
\exp\!\left[
-\alpha\frac{C_u+C_v}{2}
-\frac{\beta}{2}
\lVert D_u(C)-D_v(C)\rVert^2
-\frac{\gamma}{2}J_e^2
\right]
\right).
$$

$D_i(C)$ denotes the admitted deterministic graph differential summary. The GRC-v3 induced-frame backend is the present graph-generic reference; the GRC9 fixed row-basis backend remains specialization content. The functional itself contains no ordered-port or $3\times3$-chart premise.

The current promoted profile is exactly the accepted curvature-disabled D7 law. A future curvature-conditioned law is not an editorial elaboration of this equation. It requires a new complete-profile identity, new provenance, and reopening of the earliest affected constitutive and staging contracts.

$W_{\mathrm{floor}}>0$ is load-bearing. It preserves the declared positive domain and introduces a nonsmooth floor boundary. Classical derivatives used by local CI, OS, or analysis results apply only on the stated floor-inactive chart unless the accepted source gives a one-sided or tangent-cone treatment.

> **Primary source object:** `A-GW-FUNCTIONAL`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-GW-FUNCTIONAL`.

### 8.4 Pre-read instantaneous reference

The accepted pre-read reference is

$$
\widehat W_{A,k}
=
G_W\!\left(C_k,J_{0,A,k}\right).
$$

Its stage is load-bearing. $\widehat W_{A,k}$ is constructed after the current profile has produced the fresh baseline $J_{0,A,k}$ and before $q_{A,k}$ is evaluated. It is not:

- an independently retained state;
- the incoming value of $W_A$;
- the post-continuity write target;
- a next-beat prediction;
- a stale prior-current cache.

For fixed-reference or PC profiles, this equation is evaluated at the geometry supplied by the complete profile. In CI, $\widehat W_A(h)$ is recomputed inside every joint-root residual evaluation after $J_{0,A}(h)$. In OS, it is recomputed from the corrected geometry and corrected baseline rather than reused from the predictor. These realization-specific stages are stated in §10.

> **Primary source object:** `A-WHAT`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-WHAT`.

### 8.5 Directional contrast

The retained relation is

$$
q_{A,e}
=
\frac{
W_{A,e}-\widehat W_{A,e}
}{
W_{A,e}+\widehat W_{A,e}
}.
$$

Positivity of $W_A$ and $\widehat W_A$ gives a nonzero denominator on the accepted domain. $q_A$ is a signed relation between an authoritative retained mobility and a derived instantaneous reference. It is not itself a retained coordinate, a current, or a writer.

A change in $q_A$ has two possible causes:

```text
authoritative-state motion:
  W_A changes under its accepted writer while the comparison is controlled

reference-surface motion:
  W_hat_A changes because C, geometry, or baseline current changes
```

Only the first route directly supports an A carrier-write or release attribution. Relation neutralization by a moving reference is not automatically a retained-state write.

> **Primary source object:** `A-DIRECTIONAL-CONTRAST`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-DIRECTIONAL-CONTRAST`.

### 8.6 Read-Back and total-current closure

In physical flux coordinates, the accepted A read is elementwise:

$$
j_{A,\mathrm{flux}}
=
\chi_A\operatorname{Diag}(q_A)J_{C,A},
$$

or, edge by edge,

$$
j_{A,e}
=
\chi_A q_{A,e}J_{C,A,e}.
$$

The authoritative current satisfies

$$
J_{C,A}
=
J_{0,A}
+
\zeta_A j_{A,\mathrm{flux}}.
$$

On the fixed-geometry algebraic A profile this gives

$$
J_{C,A,e}
=
\frac{
J_{0,A,e}
}{
1-\zeta_A\chi_A q_{A,e}
}.
$$

The accepted sufficient uniform region is

$$
0\leq \zeta_A\leq \overline\zeta_A<1,
$$

which yields the corresponding diagonal inverse margin on the admitted positive A domain. Exact realization-local regularity may impose additional geometry, floor, and joint-root conditions.

The binary-gate on/off difference at a matched admissible state is

$$
J_{C,A}(\chi_A=1)
-
J_{C,A}(\chi_A=0)
=
\frac{
\zeta_A q_A J_{0,A}
}{
1-\zeta_A q_A
},
$$

understood edgewise on the fixed-geometry profile. This proves constitutive sensitivity of the explicit read arrow when the baseline, contrast, gate, gain, and downstream sensitivity are nonzero. It does not prove empirical physical nonabsorbability or a nonzero committed endpoint effect on every fixture.

The decomposition gauge is fixed. $J_{0,A}$ includes the direct $W_A$ mobility and admitted geometry-conditioned baseline; $j_A$ is the explicit relation-conditioned read. Terms may not be reassigned between them after observing the result.

> **Primary source object:** `A-READ-CLOSURE`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-READ-CLOSURE`.

> **Claim boundary:** the A profile is admitted by `D10-CL-O-001`; physical nonabsorbability remains conditional under `D10-CL-C-007`.

### 8.7 Structural source from the A read

The structural branch first lowers the physical read current with the accepted flux flat map:

$$
j_A^\flat
=
G_J(h)\,j_{A,\mathrm{flux}}.
$$

The accepted A structural source is

$$
S_A(J,h)
\equiv
\Delta K_{4,A}(J,h)
=
\zeta_A\,
\iota_A\!\left(
\mathcal A_\star(j_A^\flat)
\right).
$$

$\mathcal A_\star$ and $\iota_A$ are the accepted typed structural-source and embedding interfaces. $\zeta_A$ is external to $\iota_A$; the equation therefore assumes no unstated homogeneity of the adapter. The source is $K_4$-valued. It is not itself $H_{1,\mathrm{form}}$, $h_4$, transport mobility, or a committed persistent carrier.

The realization decides how this source is consumed:

- CI places it inside the simultaneous current/geometry root;
- OS builds one predictor geometry from it and performs one fixed-geometry corrector;
- RG2b evaluates the accepted reconstructed section;
- PC writes it into the persistent carrier for future geometry;
- CI+PC consumes it immediately and writes the same root source into the persistent carrier.

A same-beat source record without an admitted geometry consumer is not structural cultivation. Conversely, a geometry consumer does not make the source a second current or resource transfer.

> **Primary source objects:** `GEOM-ASSEMBLY`, `REAL-CI`.

> **Equation/contract rows:** `D10.2-EC-PARENT-GEOM-ASSEMBLY`, `D10.2-EC-GEOM-K4-ASSEMBLY`, `D10.2-EC-CI-A-ROOT`.

> **Associated accepted claims:** `D10-CL-N-006`, `D10-CL-O-003`.

### 8.8 Continuity and post-continuity writer target

After the complete profile has produced one authoritative $J_{C,A,k}$, continuity writes the resource state exactly once:

$$
C_{k+1}
=
C_k
-
\Delta t_k\,B J_{C,A,k}
+
B_{\mathrm{ext},k}
+
S_{\mathrm{ext},k}.
$$

The ordinary resource domain and charge budget are validated before a final-$C$-dependent writer consumes the post-continuity state. Every graph differential summary required by $G_W$ is then refreshed from $C_{k+1}$. The write target is

$$
W_{\mathrm{drv},A,k}
=
G_W\!\left(
C_{k+1},
J_{C,A,k}
\right).
$$

The accepted downstream mediator is therefore the staged pair

$$
\mathcal D_{A,k}
=
\bigl(
C_{k+1},
J_{C,A,k}
\bigr),
$$

together with the freshly reconstructed differential backend context. The writer may not use:

- pre-continuity $C_k$ differential caches;
- diagnostic $j_A$ in place of $J_{C,A}$;
- a stale or incoming current;
- a future next-beat current;
- an uncommitted geometry from a different realization;
- a direct second write to $C$.

> **Primary source object:** `A-WRITER-TARGET`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-WRITER-TARGET`.

### 8.9 Retained mobility writer

Let

$$
a_{A,k}
=
\exp\!\left(
-\frac{\Delta t_k}{\tau_A}
\right),
\qquad
0<a_{A,k}<1.
$$

The accepted retained write is

$$
\log W_{A,k+1}
=
a_{A,k}\log W_{A,k}
+
\bigl(1-a_{A,k}\bigr)
\log W_{\mathrm{drv},A,k},
$$

or equivalently,

$$
W_{A,k+1}
=
W_{A,k}^{\,a_{A,k}}
W_{\mathrm{drv},A,k}^{\,1-a_{A,k}},
$$

with powers understood componentwise on the positive edge field.

This is one writer, not three ordered update operators. Its logarithmic increment is

$$
\Delta\log W_A
=
\bigl(1-a_A\bigr)
\bigl(
\log W_{\mathrm{drv},A}
-
\log W_A
\bigr).
$$

The geometric interpolation preserves the accepted positive multiplicative domain when both inputs lie in that domain. It introduces no hidden optimizer, queue, prior target, clipping history, or post-update global normalization.

New $W_{A,k+1}$ cannot re-enter the beat-$k$ current solve. A profile that allows same-beat new-$W$ feedback would change the Markov state, derivative, root, and branch contract and therefore requires a new identity.

> **Primary source object:** `A-RETAINED-WRITER`.

> **Equation/contract row:** `D10.2-EC-PARENT-A-RETAINED-WRITER`.

### 8.10 Formation, retention, and release in A

The accepted writer gives formation, retention, and release precise candidate-local meanings.

**Formation** is an attributable writer difference under a matched zero-forming-current control. The current-sensitive term in $G_W(C_{k+1},J_{C,A,k})$ changes $W_{\mathrm{drv},A,k}$ and therefore changes the authoritative $W_{A,k+1}$. Initialization of a nonneutral $W_A$ is not native formation.

**Retention** is the future causal availability of the nonneutral $W_A$ after the forming driver is absent. For a stationary no-forming target, the logarithmic residual is carried by $a_A$ per beat and continues to affect mobility, baseline current, relation, total current, and later writes while nonzero.

**Release** is the accepted convergence of that residual toward the stationary no-forming target under repeated no-forming-current beats. It is not administrative reset, clipping, silent overwrite, or an external cleanup producer.

A large $\tau_A$ or $a_A$ close to one is not evidence of formation or causal retention by itself. The design equation establishes a lawful retained transition. Runtime-reached formation, persistence, release, replay, and channel attribution remain verification obligations.

The complete direct retained-mobility recurrence is

```text
W_A,k
  -> Phi_A,k and J0_A,k
  -> J_C,A,k
  -> C_k+1 and W_drv,A,k
  -> W_A,k+1.
```

The explicit Read-Back-participating subloop is

```text
W_A,k and W_hat_A,k
  -> q_A,k
  -> j_A,k
  -> J_C,A,k
  -> C_k+1 and W_drv,A,k
  -> W_A,k+1.
```

Setting $\chi_A=0$ opens the explicit subloop while leaving the direct retained-mobility recurrence potentially active. This is why “read off” and “history off” are not interchangeable controls.

### 8.11 Initialization, migration, and lifecycle binding

The graph-generic history-free A initializer is a typed target-profile operation:

```text
target graph and context
  -> rebuild the declared deterministic target differential surfaces
  -> evaluate the accepted curvature-disabled G_W reference stage
  -> construct target W_A without source-profile A history
  -> perform target-profile readmission
  -> emit the direction-specific history-loss receipt
```

This initializer role is GRC-derived. The exact GRC9V3 base-conductance reconstruction used by the GRC9V4 specialization is a separate specialization binding and belongs in Appendix A.

An A profile migration must transform or reconstruct:

- current $C$;
- reset $C$;
- current and reset $W_A$ where the target retains A history;
- realization-specific $Z_{4,A}$ where applicable;
- graph, context, profile identity, and $Q_{\mathrm{target}}$;
- information-loss and charge receipts.

Generic migration grammar does not select an initializer, preserve history automatically, or permit in-place reinterpretation of bytes under a new profile identity.

### 8.12 Candidate A controls and claim ceiling

The A family requires separate controls for:

- passive zero current;
- no forming input;
- read off, $\chi_A=0$;
- causal gain off, $\zeta_A=0$;
- writer off after an otherwise valid beat;
- retained-state frozen;
- carrier-neutral matched prepared state;
- direct retained-mobility path versus explicit read path;
- graph reorientation versus physical current-history reversal;
- post-continuity writer refresh;
- floor-active versus floor-inactive charts;
- initialization versus native formation;
- administrative reset versus native release;
- explicit-channel absorbability;
- realization-specific geometry consumption;
- topology, boundary, and cache rivals.

The accepted A content establishes:

- positive authoritative $W_A$;
- an accepted graph-generic curvature-disabled $G_W$;
- a staged instantaneous reference;
- a signed retained relation;
- regular total-current closure on its declared domain;
- one continuity write;
- one positive retained writer;
- a typed structural source;
- compatibility with each admitted realization under that realization’s own contract.

It does not establish:

- that A is inherited core;
- that A is preferred or unique;
- a universal physical unit interpretation;
- physical nonabsorbability of the explicit read channel;
- formed-branch reachability;
- runtime formation, post-input retention, or release;
- nonzero committed endpoint hysteresis;
- structural or temporal stability;
- validity through the floor boundary or a current singularity;
- a direct $h_4\mapsto W_A$ constitutive map.

No new successor investigation is required merely because these stronger statements remain open. A successor is activated only if the intended proposal must make one of them as a central positive claim.


---

## 9. Constitutive Family C: Derived $C$-Sector Hodge Response

Candidate C is the admitted revision-specific family in which an accepted sector selected from authoritative $C$ conditions a typed graph-Hodge response and hence the present physical current. The sector, selector, Hodge objects, identifications, resolvent, and read surfaces are derived. Candidate C does not add an independent retained coordinate merely to duplicate the information already carried by $C$.

This distinction is central:

```text
formal recurrence of a selected sector
  is not automatically
independent dynamical retention in a new state coordinate.
```

C nevertheless supplies a complete candidate-local transition because continuity writes $C$, the selected sector and Hodge package are rederived from the new $C$, and the resulting response can alter later current. The paper may describe this accepted resource-mediated write/read closure. It must not turn $T_C$ into hidden state or claim that the selected sector has demonstrated runtime post-input memory.

### 9.1 Authoritative state and derived chain

For a C profile without a realization-specific persistent carrier, the independent candidate state is

$$
X_{C,k}
=
C_k,
$$

together with graph, context, complete-profile identity, reset state, charge target, and lifecycle metadata. A PC or CI+PC realization adds its declared $Z_{4,C}$ state through the realization axis. Candidate C itself writes no independent $T_C$, selector, Hodge, response, geometry, or current coordinate.

The accepted derived chain is

```text
authoritative C
  -> selector P_M
  -> selected sector T_C
  -> retained Hodge package H_M
  -> selected/physical identification I_4M
  -> Hodge Laplacian Delta_1,M
  -> ungated intrinsic resolvent Rhat_C,M
  -> once-gated physical Read-Back
  -> authoritative current
  -> continuity writes C
  -> all C-derived surfaces are rederived.
```

The selector and Hodge package may be same-step functions of the realization geometry $h$. In CI they are evaluated inside the joint residual. In OS they are recomputed at the corrected geometry. In RG2b they are evaluated on the reconstructed section. In PC they are evaluated on the geometry generated by the committed carrier. These timing differences do not alter the C authority rule.

> **Primary source object:** `C-AUTHORITY`.

> **Equation/contract rows:** `D10.2-EC-PARENT-C-AUTHORITY`, `D10.2-EC-C-AUTHORITY`.

> **Associated accepted claims:** normative authority claim `D10-CL-N-002`; Candidate C is admitted under `D10-CL-O-002`.

### 9.2 Basis-independent selector and selected sector

On the accepted reference graph-Hodge package, form the symmetric vertex operator

$$
L_{0,\mathrm{sym,pre}}
=
H_{0,\mathrm{pre}}^{-1/2}
B_{\mathrm{pre}}
H_{1,\mathrm{form,pre}}
B_{\mathrm{pre}}^\top
H_{0,\mathrm{pre}}^{-1/2}.
$$

For the declared threshold $\Lambda_C$, define the basis-independent spectral selector

$$
Q_M
=
\mathbf 1_{[0,\Lambda_C]}
\!\left(
L_{0,\mathrm{sym,pre}}
\right),
$$

and transfer it to the physical vertex coordinates as

$$
P_M^\Delta
=
H_{0,\mathrm{pre}}^{-1/2}
Q_M
H_{0,\mathrm{pre}}^{1/2}.
$$

The selected content is

$$
T_{C,k}
=
P_M^\Delta C_k.
$$

The current accepted smooth stratum requires fixed topology and boundary semantics together with either:

- a fixed-rank selector under a strict spectral gap, or
- an explicitly declared boundary rule that determines what happens at the cutoff.

For a rank-$m$ fixed selector, the smooth chart requires

$$
\lambda_m
<
\Lambda_C
<
\lambda_{m+1}.
$$

The normalized cutoff may be written in the accepted profile form

$$
\Lambda_C
=
\overline\Lambda_C\,
\sigma_{L,\mathrm{pre}},
$$

where the scale and cutoff are profile-local and serialized. The selection is not chosen from an eigenvector basis after the fact; it is the functional-calculus projector of the declared symmetric operator.

When the complete profile makes the selector geometry-dependent, the notation $P_M(h)$ and

$$
T_C(h)
=
P_M(h)C_k
$$

must retain the full causal path

```text
h -> P_M(h) -> T_C(h).
```

Omitting that path from a derivative or residual would remove a load-bearing dependence.

Selector-rank change, loss of gap, topology change, boundary change, or an undeclared cutoff tie is not an ordinary smooth C beat. It activates fail-closed or typed event/successor semantics.

> **Primary source objects:** `C-SECTOR`, `C-SELECTOR`.

> **Equation/contract rows:** `D10.2-EC-PARENT-C-SECTOR`, `D10.2-EC-PARENT-C-SELECTOR`, `D10.2-EC-C-SECTOR`.

### 9.3 Selected content to retained Hodge package

The accepted C construction first normalizes the selected vertex content:

$$
\rho_{C,v}
=
\tanh\!\left(
\frac{T_{C,v}}{C_{\mathrm{ref}}}
\right).
$$

For an oriented edge $e=(u,v)$, define the sign-even edge content

$$
r_{C,e}
=
\frac{
\rho_{C,u}+\rho_{C,v}
}{2}.
$$

The positive diagonal modulation is

$$
D_C
=
\operatorname{Diag}\!\left(
\exp\!\left[
\frac{\kappa_{M,C}}{2}r_C
\right]
\right).
$$

The retained Hodge package is then

$$
H_{0,M}
=
H_{0,\mathrm{pre}},
$$

$$
H_{1,\mathrm{form},M}
=
D_C
H_{1,\mathrm{form,pre}}
D_C.
$$

Equivalently, its logarithmic edge modulation satisfies

$$
\log(D_C^2)
=
\kappa_{M,C}\operatorname{Diag}(r_C).
$$

The map is positive on the accepted finite selected-content domain. It assigns the selected C content constitutive authority over the one-form Hodge package without making $T_C$ or $H_{1,\mathrm{form},M}$ an independently written coordinate.

$\kappa_{M,C}=0$ removes the retained-content modulation and returns the reference Hodge package. This is a geometry-condition ablation. It is not automatically the same as $\chi_C=0$, which removes explicit causal Read-Back while leaving the conditioned baseline geometry available where the profile declares it.

The C modulation is sign-even with respect to arbitrary stored-edge coordinate reversal. That coordinate covariance does not imply invariance under a physical reversal of the activity history, because such a reversal may change $C$ and hence the selected content.

> **Primary source object:** `C-HODGE-MAPS`.

> **Equation/contract row:** `D10.2-EC-PARENT-C-HODGE-MAPS`.

### 9.4 Selected/physical identification and Hodge Laplacian

The accepted selected-to-physical one-form identification is

$$
I_{4M}
=
H_{1,\mathrm{form},M}
H_{1,\mathrm{form,pre}}^{-1},
$$

with inverse

$$
I_{4M}^{-1}
=
H_{1,\mathrm{form,pre}}
H_{1,\mathrm{form},M}^{-1}.
$$

When geometry is active, the full notation is

$$
I_{4M}
=
I_{4M}(T_C,h),
$$

because both the selected content and the current geometry can affect the Hodge package. This explicit dependence is load-bearing in CI and OS.

The accepted one-form Hodge Laplacian on the admitted selected one-form space is

$$
\Delta_{1,M}
=
B^\top
H_{0,M}^{-1}
B
H_{1,\mathrm{form},M}.
$$

Its domain, codomain, and metric are part of the profile. Equal matrix dimensions do not permit the selected, physical-flux, and structural-flat spaces to be identified without the accepted maps.

> **Primary source object:** `C-HODGE-MAPS`.

> **Equation/contract row:** `D10.2-EC-C-HODGE-LAPLACIAN`.

### 9.5 Ungated resolvent and once-gated Read-Back

The final accepted intrinsic C response is the **ungated** resolvent

$$
\widehat R_{C,M}
=
\left(
I+\tau_C\Delta_{1,M}
\right)^{-1}.
$$

The hat is used here to keep the final convention visible. Historical D5-v2 notation placed $\chi_C$ inside a symbol called $R_{C,M}$. D6-v2, D7-v2, the accepted realization records, and D10.2 use an ungated intrinsic response and apply $\chi_C$ exactly once to the causal read. The proposal follows the final accepted convention and does not combine the two notations.

For physical flux current $J$, first lower it with the accepted structural flat map and transfer it to the selected retained coordinates. The intrinsic response is

$$
r_C^\flat(J,h)
=
I_{4M}(T_C,h)^{-1}
\widehat R_{C,M}(T_C,h)
I_{4M}(T_C,h)
G_J(h)J.
$$

The causal read is

$$
j_C^\flat(J,h)
=
\chi_C\,r_C^\flat(J,h),
$$

and its physical-flux representation is

$$
j_{C,\mathrm{flux}}(J,h)
=
G_J(h)^{-1}
j_C^\flat(J,h).
$$

This chain preserves four distinct operations:

```text
physical flux J
  -> structural flat current G_J(h)J
  -> selected-coordinate identification I_4M
  -> intrinsic resolvent Rhat_C,M
  -> inverse identification
  -> one causal gate chi_C
  -> physical-flux sharp map.
```

$\widehat R_{C,M}$ may remain a diagnostic intrinsic response when $\chi_C=0$, but it has no explicit causal read consumer. A second multiplication by $\chi_C$ anywhere in the resolvent, structural source, or total-current equation would change the accepted profile.

> **Primary source object:** `C-READ-BACK`.

> **Equation/contract rows:** `D10.2-EC-PARENT-C-READ-BACK`, `D10.2-EC-C-RESOLVENT`, `D10.2-EC-C-READBACK`.

### 9.6 Fixed-geometry total-current closure and regularity

At fixed admitted geometry, the C physical current satisfies

$$
J_{C,C}
=
J_{0,C}
+
\zeta_C
j_{C,\mathrm{flux}}(J_{C,C},h).
$$

In the selected one-form coordinates, let

$$
R_{C,M}
\equiv
\widehat R_{C,M}
=
\left(
I+\tau_C\Delta_{1,M}
\right)^{-1}.
$$

The accepted post-v2 Hodge correction requires the full physical-flux to selected-form identification

$$
Q_C(T_C,h)
=
I_{4M}(T_C,h)
G_J(h).
$$

The corresponding ungated physical-flux response is

$$
\widehat R_{C,\mathrm{flux}}(T_C,h)
=
Q_C(T_C,h)^{-1}
\widehat R_{C,M}(T_C,h)
Q_C(T_C,h).
$$

Thus the physical algebraic closure is

$$
J_{C,C}
=
J_{0,C}
+
\zeta_C\chi_C
\widehat R_{C,\mathrm{flux}}J_{C,C},
$$

hence

$$
L_{C,\mathrm{flux}}
=
I-\zeta_C\chi_C\widehat R_{C,\mathrm{flux}},
$$

$$
J_{C,C}
=
L_{C,\mathrm{flux}}^{-1}J_{0,C},
$$

on the exact regular domain.

If $\nu_i$ are the nonnegative eigenvalues of the accepted retained-coordinate Hodge Laplacian, then the intrinsic response eigenvalues are

$$
r_i
=
\frac{1}{1+\tau_C\nu_i}.
$$

The exact retained-coordinate regularity condition is

$$
1-\zeta_C\chi_C r_i
\neq 0
\qquad
\text{for every admitted mode }i.
$$

For the accepted nonnegative-gain profile,

$$
\tau_C>0,
\qquad
0\leq\zeta_C\leq\overline\zeta_C<1,
$$

provides the retained-coordinate inverse margin. Harmonic modes have $r_i=1$, so $\zeta_C\chi_C=1$ is singular and remains outside the admitted profile.

Exact physical-flux invertibility transfers by similarity, not by equality of singular values:

$$
L_{C,\mathrm{flux}}
=
Q_C^{-1}
\left(
I-\zeta_C\chi_C\widehat R_{C,M}
\right)
Q_C.
$$

At the reference geometry, define

$$
Q_{C,\mathrm{ref}}
=
I_{4M}(T_{C,\mathrm{ref}},h_{\mathrm{ref}})
G_J(h_{\mathrm{ref}}),
$$

$$
\widehat R_{C,\mathrm{flux,ref}}
=
Q_{C,\mathrm{ref}}^{-1}
\widehat R_{C,M,\mathrm{ref}}
Q_{C,\mathrm{ref}},
$$

and

$$
L_{C,\mathrm{flux,ref}}
=
I-\zeta_C\chi_C
\widehat R_{C,\mathrm{flux,ref}}.
$$

Then

$$
L_{C,\mathrm{flux,ref}}
=
Q_{C,\mathrm{ref}}^{-1}
\left(
I-\zeta_C\chi_C
\widehat R_{C,M,\mathrm{ref}}
\right)
Q_{C,\mathrm{ref}}.
$$

Exact invertibility therefore transfers. The retained singular-value margin does not transfer unchanged. A physical inverse estimate additionally depends on the identification condition number:

$$
\left\|
L_{C,\mathrm{flux,ref}}^{-1}
\right\|
\leq
\frac{
\operatorname{cond}(Q_{C,\mathrm{ref}})
}{
1-\overline\zeta_C
},
$$

under the accepted retained contraction bound and finite identification condition number.

This distinction prevents a retained-space positivity or contraction result from being mislabeled as a physical Euclidean norm theorem.

> **Type-correction source:** accepted `D7GPostv2GraphHodgeTypeCorrection` and its downstream CI realization.

> **Associated conditional boundary:** general physical conditioning and executable solver behavior remain conditional under `D10-CL-C-006`.

### 9.7 Structural source from the C read

The accepted C structural source is

$$
S_C(J,h)
\equiv
\Delta K_{4,C}(J,h)
=
\zeta_C\,
\iota_C\!\left(
\mathcal A_\star(j_C^\flat(J,h))
\right).
$$

As in A, $\zeta_C$ is external to $\iota_C$ and is applied once. $\chi_C$ has already been applied once in $j_C^\flat$ and is not repeated inside the source.

The exact switch contracts are:

```text
chi_C = 0
  -> j_C^flat = 0
  -> j_C,flux = 0
  -> no read-derived structural source

zeta_C = 0
  -> authoritative current reduces to J0_C
  -> no read-derived structural source
```

An ungated intrinsic response $r_C^\flat$ may remain diagnostically defined under $\zeta_C=0$, but it has no causal consumer. The $K_4$ source is consumed according to the realization in §10 and is not itself a committed C state coordinate.

> **Primary source objects:** `GEOM-ASSEMBLY`, `REAL-CI`.

> **Equation/contract rows:** `D10.2-EC-PARENT-GEOM-ASSEMBLY`, `D10.2-EC-GEOM-K4-ASSEMBLY`, `D10.2-EC-CI-C-ROOT`.

> **Associated accepted claims:** `D10-CL-N-006`, `D10-CL-O-003`.

### 9.8 Write-back through authoritative $C$

After the complete profile has produced one authoritative $J_{C,C,k}$, continuity writes

$$
C_{k+1}
=
C_k
-
\Delta t_k\,B J_{C,C,k}
+
B_{\mathrm{ext},k}
+
S_{\mathrm{ext},k}.
$$

Candidate C has no second independent writer. Its future selected content is rederived:

$$
T_{C,k+1}
=
P_{M,k+1}^\Delta C_{k+1}.
$$

The exact bookkeeping identity is

$$
T_{C,k+1}-T_{C,k}
=
P_{M,k}^\Delta
\bigl(
C_{k+1}-C_k
\bigr)
+
\bigl(
P_{M,k+1}^\Delta-P_{M,k}^\Delta
\bigr)
C_{k+1}.
$$

The first term is selected content change under the old selector. The second is selector or basis motion. These two mechanisms must be reported separately. On a fixed-selector stratum the second term vanishes, giving

$$
T_{C,k+1}-T_{C,k}
=
P_M^\Delta
\bigl(
C_{k+1}-C_k
\bigr).
$$

All future C surfaces are then rederived in the accepted order:

```text
C_k+1
  -> P_M,k+1
  -> T_C,k+1
  -> H_M,k+1
  -> I_4M,k+1 and Delta_1,M,k+1
  -> Rhat_C,M,k+1
  -> future Read-Back.
```

This is a complete resource-mediated write/read recurrence. It does not authorize a hidden $T_C$ writer, holding $T_C$ fixed while $C$ and its selector evolve off-manifold, or calling generic projector motion “retained formation.”

### 9.9 Candidate C controls

Candidate C requires controls that respect its derived-state ontology:

- $\kappa_{M,C}=0$ removes selected-content Hodge modulation;
- $\chi_C=0$ removes the explicit causal read while preserving any declared conditioned baseline;
- $\zeta_C=0$ removes the read contribution from authoritative current and structural source;
- matched selected-content versus matched-complement interventions test whether selected content is load-bearing;
- fixed-rank and strict-gap controls isolate smooth selector strata;
- selector-motion and selected-content-change terms are reported separately;
- physical current-history reversal is distinct from edge-coordinate reversal;
- a derived response cache cannot be altered independently;
- a frozen $T_C$ counterfactual is admissible only if it corresponds to a lawful matched authoritative $C$ state;
- topology, boundary, graph measure, and context rivals remain explicit;
- retained-coordinate conditioning and physical-flux conditioning remain separately reported.

There is no generic C `write_off` switch analogous to disabling A’s independent mobility writer. Turning off continuity would alter the resource dynamics, not isolate a separate C writer. A lawful write attribution must therefore use matched current or matched authoritative-$C$ interventions within the declared profile.

### 9.10 Candidate C claim ceiling

The accepted C content establishes:

- $C$-only candidate authority;
- a basis-independent selected-sector contract;
- a positive retained Hodge package on the admitted domain;
- typed selected/physical identifications;
- an ungated regular resolvent;
- a once-gated physical Read-Back;
- exact fixed-geometry current regularity under the accepted bounds;
- a typed $K_4$ structural source;
- resource-mediated future rederivation;
- compatibility with each admitted realization under its own domain and stage contract.

It does not establish:

- an independent $T_C$ or Hodge history state;
- smooth passage through selector-rank or topology boundaries;
- physical nonabsorbability of the C read;
- an unchanged physical singular-value margin under non-isometric identification;
- runtime selected-sector formation, retention, release, or mediation;
- a general nonidentity committed endpoint effect;
- global coupled-root uniqueness;
- structural or temporal stability;
- that C is preferred, unique, or inherited core.

The phrase “retained sector” in the proposal must therefore refer to the accepted constitutive role and cross-beat resource-mediated recurrence, not to an additional serialized carrier or an already demonstrated post-input memory regime. This boundary is presently expressible without a new successor investigation.


---

## 10. Geometry-Temporal Realization Families

The constitutive family and the geometry-temporal realization answer different questions.

A constitutive family specifies:

```text
what representation conditions the present beat;
how it is read into current;
what candidate state is authoritative;
what transition makes the representation available later.
```

A realization specifies:

```text
when generated geometry is consumed;
whether current and geometry are solved simultaneously or in stages;
whether geometry is reconstructed from candidate state;
whether an independent K_4 history carrier persists;
how realization-local failure, reset, and migration behave.
```

The accepted initial population contains five realizations:

$$
\mathrm{CI},\qquad
\mathrm{OS},\qquad
\mathrm{RG2b},\qquad
\mathrm{PC},\qquad
\mathrm{CI+PC}.
$$

Each is crossed with A and C. The resulting ten complete profiles are distinct because their state, stage order, root or reconstruction law, history authority, and lifecycle consequences differ. They are not ranked, and they are not a theorem that every possible GRC-v4 realization belongs to this list.

### 10.1 Common realization interfaces

For candidate $a\in\{A,C\}$, let:

- $X_{a,k}$ be the authoritative candidate state at beat $k$;
- $U_k$ be the declared same-step input and fixed profile context;
- $J_{0,a}$ be the candidate-specific baseline current;
- $j_{a,\mathrm{flux}}$ be the accepted explicit Read-Back current in physical flux coordinates;
- $S_a(J,h)=\Delta K_{4,a}(J,h)$ be the accepted $K_4$-valued structural source;
- $H_{\mathrm{profile}}$ be the accepted geometry profile;
- $\Phi_a$ be the complete candidate transition and commit map.

These symbols name accepted interfaces. They do not erase the different A and C equations. In particular:

- A retains authoritative $W_A$ and writes it after continuity;
- C writes only $C$ and rederives its selected sector and Hodge package;
- the selected realization may add $Z_{4,a}$ to the state;
- only final authoritative physical current enters continuity;
- current, geometry, selectors, and response objects are same-step derived unless a complete profile explicitly makes a structural carrier authoritative.

Every realization is fail-closed. A domain loss, singular or underconditioned required block, missing or multiple inadmissible root, nonfinite result, failed residual or reconstruction condition, failed charge or state validation, or departure from the declared chart commits nothing.

### 10.2 Coupled Implicit — CI

CI closes current and generated geometry simultaneously. Its joint same-step unknown is

$$
Y_a
=
(J_a,h_a),
$$

or the equivalent typed tuple used by the profile. The root contract is

$$
F_a(Y_a;X_{a,k},U_k)
=
0.
$$

$J_a$ and $h_a$ are algebraic variables of the current beat. They are not persistent state. Only the unique regular local branch connected to the accepted $\kappa_H=0$ reference branch is admitted.

> **Primary source object:** `REAL-CI`.

> **Equation/contract parent row:** `D10.2-EC-PARENT-REAL-CI`.

> **Associated accepted profile claim:** `D10-CL-O-003`.

#### 10.2.1 Candidate A CI root

Candidate A uses the reference-relative geometry consumer from §8.2:

$$
\Delta_0(h)
=
H_{0,\mathrm{ref}}^{-1}
B
H_{1,\mathrm{form}}(h)
B^\top,
$$

$$
\Phi_A^{CI}(C,W_A,h)
=
\Phi_A^{D7}(C,W_A)
+
\kappa_{Ah}
\bigl[
\Delta_0(h)-\Delta_0(h_{\mathrm{ref}})
\bigr]C,
$$

$$
J_{0,A}^{CI}(C,W_A,h)
=
-M_{4,A}(W_A)d_0\Phi_A^{CI}(C,W_A,h).
$$

Inside every residual evaluation, in this order, it reconstructs

$$
\widehat W_A(h)
=
G_W\!\left(
C_k,
J_{0,A}^{CI}(C_k,W_{A,k},h)
\right),
$$

$$
q_A(h)
=
\frac{
W_{A,k}-\widehat W_A(h)
}{
W_{A,k}+\widehat W_A(h)
},
$$

$$
j_{A,\mathrm{flux}}(J,h)
=
\chi_A
\operatorname{Diag}\!\bigl(q_A(h)\bigr)J,
$$

$$
j_A^\flat(J,h)
=
G_J(h)j_{A,\mathrm{flux}}(J,h),
$$

$$
S_A(J,h)
=
\Delta K_{4,A}(J,h)
=
\zeta_A
\iota_A\!\left(
\mathcal A_\star(j_A^\flat(J,h))
\right).
$$

The joint root is

$$
F_{J,A}
=
J
-
J_{0,A}^{CI}(C_k,W_{A,k},h)
-
\zeta_A j_{A,\mathrm{flux}}(J,h)
=
0,
$$

$$
F_{h,A}
=
h
-
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
S_A(J,h),
h_{4,\mathrm{ref}},
U_k
\right)
=
0.
$$

$\widehat W_A(h)$ is not frozen outside the root. Reusing a value from a prior residual evaluation would alter the derivative and root map. After a regular root, only $J_A^\star$ enters continuity; the unchanged post-continuity A writer then produces $W_{A,k+1}$.

The admitted A-CI branch is the unique local branch selected by the preregistered bounded self-map and contraction conditions and connected to the $\kappa_H=0$ reference solution. The contraction result is local and profile-specific. It does not imply global uniqueness, global convergence from arbitrary solver seeds, or stability of the complete transition.

> **Equation/contract rows:** `D10.2-EC-CI-A-ROOT`, `D10.2-EC-CI-A-CONTRACTION`.

#### 10.2.2 Candidate C CI root

For Candidate C, every trial geometry carries the full accepted chain

```text
h
  -> P_M(h)
  -> T_C(h)=P_M(h)C_k
  -> H_M(T_C,h)
  -> I_4M(T_C,h)
  -> Delta_1,M(T_C,h)
  -> Rhat_C,M(T_C,h).
```

The read and source are

$$
r_C^\flat(J,h)
=
I_{4M}(T_C,h)^{-1}
\widehat R_{C,M}(T_C,h)
I_{4M}(T_C,h)
G_J(h)J,
$$

$$
j_C^\flat(J,h)
=
\chi_C r_C^\flat(J,h),
$$

$$
j_{C,\mathrm{flux}}(J,h)
=
G_J(h)^{-1}j_C^\flat(J,h),
$$

$$
S_C(J,h)
=
\Delta K_{4,C}(J,h)
=
\zeta_C
\iota_C\!\left(
\mathcal A_\star(j_C^\flat(J,h))
\right).
$$

The C joint root is

$$
F_{J,C}
=
J
-
J_{0,C}(C_k,T_C(h),h,U_k)
-
\zeta_Cj_{C,\mathrm{flux}}(J,h)
=
0,
$$

$$
F_{h,C}
=
h
-
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
S_C(J,h),
h_{4,\mathrm{ref}},
U_k
\right)
=
0.
$$

The accepted local theorem applies on a fixed-topology, smooth SPD, fixed-selector-rank stratum with strict gap and regular current block. At $\kappa_H=0$ the reference joint Jacobian is block triangular with the regular physical-flux current block and identity geometry block. The implicit-function argument then supplies an existential neighborhood and a unique smooth local branch connected to that reference.

Exactly one self-consistent regular root on the preregistered branch is admitted. Zero roots, multiple regular roots without the accepted branch identity, disconnected roots, singular roots, and nonfinite roots fail closed. After a valid root, physical $J_C^\star$ enters continuity and only $C_{k+1}$ commits as candidate state. All C selector and Hodge surfaces are rederived.

> **Equation/contract rows:** `D10.2-EC-CI-C-ROOT`, `D10.2-EC-CI-C-CONTRACTION`, `D10.2-EC-CI-C-ROOT-SELECTION`.

#### 10.2.3 CI claim ceiling

CI establishes a bounded simultaneous realization for A and C. It does not establish:

- a global current/geometry branch;
- numeric branch radius;
- global root uniqueness;
- arbitrary-seed solver convergence;
- complete-step stability;
- continuation-spectrum identity;
- persistence of geometry beyond the current beat;
- an independent geometry state.

### 10.3 Operator Split — OS

OS replaces the simultaneous root with one frozen ordered pass:

```text
X_k
  -> J^(0)
  -> j_flat^(0)
  -> Delta K4^(0)
  -> h^(1)
  -> J^(1)
  -> X_(k+1).
```

There is exactly one predictor, one geometry update, one fixed-geometry corrector, and one atomic commit. $J^{(1)}$ cannot retroactively alter $h^{(1)}$. A second predictor–geometry–corrector cycle or a different order is a new complete-profile identity, not a numerical improvement to the accepted OS row.

> **Primary source object:** `REAL-OS`.

> **Equation/contract rows:** `D10.2-EC-PARENT-REAL-OS`, `D10.2-EC-OS-STAGE-ORDER`, `D10.2-EC-OS-NO-SECOND-ITERATION`.

> **Associated accepted profile claim:** `D10-CL-O-004`.

#### 10.3.1 Candidate A OS

At $h_{\mathrm{ref}}$, solve the accepted fixed-geometry A current to obtain $J_A^{(0)}$. Use the accepted once-gated read to form

$$
j_A^{\flat,(0)}
=
G_J(h_{\mathrm{ref}})
\chi_A\operatorname{Diag}(q_A^{(0)})J_A^{(0)},
$$

$$
S_A^{(0)}
=
\zeta_A
\iota_A\!\left(
\mathcal A_\star(j_A^{\flat,(0)})
\right),
$$

and

$$
h_A^{(1)}
=
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_A^{(0)}
\right).
$$

At fixed $h_A^{(1)}$, use

$$
\Phi_A^{OS}
=
\Phi_A^{D7}
+
\kappa_{Ah}
\bigl[
\Delta_0(h_A^{(1)})
-
\Delta_0(h_{\mathrm{ref}})
\bigr]C_k.
$$

Recompute, without predictor-cache authority,

```text
Phi_A^OS
  -> J0_A^OS
  -> W_hat_A
  -> q_A
  -> full fixed-h A current solve J_A^(1).
```

Only $J_A^{(1)}$ enters continuity. All writer differential summaries are refreshed from $C_{k+1}$, and the unchanged A writer produces $W_{A,k+1}$. $W_A$ remains the sole mobility authority; $h_A^{(1)}$ has no direct writer authority.

> **Equation/contract row:** `D10.2-EC-OS-A-CORRECTOR`.

#### 10.3.2 Candidate C OS

At $h_{\mathrm{ref}}$, solve

$$
J_C^{(0)}
=
J_{0,C}\!\left(
C_k,T_C(h_{\mathrm{ref}}),h_{\mathrm{ref}}
\right)
+
\zeta_C
j_{C,\mathrm{flux}}\!\left(
J_C^{(0)},h_{\mathrm{ref}}
\right).
$$

Form

$$
j_C^{\flat,(0)}
=
\chi_C
I_{4M}^{-1}
\widehat R_{C,M}
I_{4M}
G_J
J_C^{(0)},
$$

with every operator evaluated at the accepted predictor stage, then

$$
S_C^{(0)}
=
\zeta_C
\iota_C\!\left(
\mathcal A_\star(j_C^{\flat,(0)})
\right),
$$

$$
h_C^{(1)}
=
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}+S_C^{(0)}
\right).
$$

At fixed $h_C^{(1)}$, recompute the complete chain

```text
P_M
  -> T_C
  -> H_M
  -> I_4M
  -> Rhat_C,M
  -> G_J
  -> J0_C
```

and solve

$$
J_C^{(1)}
=
J_{0,C}\!\left(
C_k,T_C(h_C^{(1)}),h_C^{(1)}
\right)
+
\zeta_C
j_{C,\mathrm{flux}}\!\left(
J_C^{(1)},h_C^{(1)}
\right).
$$

Only $J_C^{(1)}$ enters continuity. Only $C_{k+1}$ commits as Candidate C state. Predictor selectors, Hodge objects, resolvents, currents, and geometry have no corrector or next-beat authority.

> **Equation/contract row:** `D10.2-EC-OS-C-CORRECTOR`.

#### 10.3.3 Split-consistency residual

The final current generally generates a different geometry from the predictor current. Define

$$
\widehat h^{(1)}
=
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
S_a(J^{(1)},h^{(1)})
\right),
$$

$$
r_{h,a}^{OS}
=
h_a^{(1)}
-
\widehat h_a^{(1)}.
$$

Let $F_a^{CI}=(F_{J,a},F_{h,a})$ be the accepted coupled root. Because the corrector solves the current equation exactly at fixed $h_a^{(1)}$,

$$
F_a^{CI}
\bigl(
J_a^{(1)},h_a^{(1)}
\bigr)
=
\bigl(
0,r_{h,a}^{OS}
\bigr).
$$

The split is therefore exactly current-consistent with the coupled constitutive equations. Its deliberate defect is the unreclosed geometry fixed point. A nonzero $r_h^{OS}$ is not automatically a failed OS step; it is reported as part of the profile’s evidence and domain contract.

On the named floor-inactive A and fixed-rank strict-gap C smooth charts, the accepted local bounds make the geometry defect quadratic in the structural coupling under the declared Lipschitz and bounded-source hypotheses. Those are conditional local bounds, not an assumption that $r_h^{OS}=O(\Delta t)$ or a uniform numerical guarantee.

> **Equation/contract row:** `D10.2-EC-OS-SPLIT-RESIDUAL`.

#### 10.3.4 OS claim ceiling

OS establishes a bounded one-pass same-beat geometry feedback realization. It does not establish:

- equality with CI;
- an iterative convergence theorem;
- zero split residual;
- an automatic $\Delta t$ truncation order;
- global regularity;
- persistent geometry history;
- nonzero committed endpoint effect merely because $h^{(1)}$ is consumed by the corrector.

### 10.4 Reconstructed Geometry — RG2b

The reconstructed-geometry investigation separated three questions.

1. An exact same-beat evaluator of the CI fixed point is CI-equivalent, not a new temporal family.
2. Local reconstruction of geometry from the poststate of an already complete CI or OS step is a property of that family, not a new realization.
3. A lagged invariant-section architecture with no persistent geometry is a genuinely distinct bounded realization. This accepted family is RG2b.

The RG2b order is

```text
X_a,k
  -> h_a,k = Gamma_a(X_a,k)
  -> accepted fixed-h current and candidate transition
  -> generated h_a,k+
  -> X_a,k+1,
```

with the invariance requirement

$$
h_{a,k+}
=
\Gamma_a(X_{a,k+1}).
$$

Let

$$
\Psi_{a,\Gamma}(X)
=
\Phi_{a,\mathrm{lag}}\!\left(
X,\Gamma(X)
\right),
$$

and

$$
G_{a,\kappa}(X,h)
=
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
S_a(C_a(h;X,U),h)
\right).
$$

The exact invariant-section equation is

$$
\Gamma_a\!\left(
\Psi_{a,\Gamma_a}(X)
\right)
=
G_{a,\kappa}\!\left(
X,\Gamma_a(X)
\right).
$$

Equivalently, the accepted graph transform fixes $\Gamma_a$:

$$
\Gamma_a
=
\mathcal T_a\Gamma_a.
$$

At $\kappa_H=0$,

$$
G_{a,0}(X,h)
=
h_{\mathrm{ref}},
$$

so

$$
\Gamma_{a,0}(X)
=
h_{\mathrm{ref}}
$$

is the exact neutral invariant section.

The positive result is relative to a frozen family-local extension profile in finite-dimensional coordinates. Choose nested compact charts

$$
K_-\Subset K\Subset U
$$

inside the admitted smooth domain. The extension agrees exactly with the candidate maps on $K$, returns to the identity state map and $h_{\mathrm{ref}}$ outside a compact neighborhood, preserves the required bounds, and is graph-relabeling and orientation equivariant. It is profile configuration, not runtime state or tuning.

On the admitted section class, the graph transform is a value-radius and Lipschitz self-map with $C^0$ contraction factor

$$
q_0<1,
$$

and the base maps satisfy the fixed-domain containment

$$
\Psi_{a,\Gamma}(K_-)
\subseteq
K.
$$

The result supplies one deterministic family-local Lipschitz section $\Gamma_a$. It serializes no $h$, previous root, branch token, solver history, or hidden continuation label. For A, $\Gamma_A$ is a deterministic function of $(C,W_A)$ and context. For C, $\Gamma_C$ is a deterministic function of $C$ and context.

> **Primary source object:** `REAL-RG2B`.

> **Equation/contract rows:** `D10.2-EC-PARENT-REAL-RG2B`, `D10.2-EC-RG-INVARIANCE`, `D10.2-EC-RG-LIPSCHITZ-CONTRACTION`, `D10.2-EC-RG-DETERMINISM`.

> **Associated accepted profile claim:** `D10-CL-O-005`.

The uniqueness is relative to the frozen extension and admitted section class. The accepted result is $C^0$/Lipschitz. A classical derivative of $\Gamma_a$, a $C^1$ invariant graph, or a continuation-spectrum claim requires a separately named successor.

> **Claim-ceiling row:** `D10.2-EC-RG-CLAIM-CEILING`.

> **Associated conditional boundary:** `D10-CL-C-009`.

### 10.5 Persistent Carrier — PC

PC adds one authoritative nonresource structural carrier to the selected candidate state. For candidate $a\in\{A,C\}$,

$$
Z_{4,a,k}
\in
\mathcal B_{R,a}
\subset
\mathcal K_{4,a}.
$$

$Z_{4,a}$ has the same candidate-specific structural type as the accepted source $S_a=\Delta K_{4,a}$. It is not full geometry, resource $C$, A mobility $W_A$, C sector $T_C$, current, solver state, or cache.

The PC read path is

$$
K_{4,a,k}
=
K_{4,\mathrm{base}}
+
Z_{4,a,k},
$$

$$
h_{a,k}
=
H_{\mathrm{profile}}\!\left(
K_{4,a,k}
\right).
$$

At fixed $h_{a,k}$, execute the accepted candidate-local current construction and form

$$
S_{a,k}
=
\Delta K_{4,a}\!\left(
J_{C,a,k},h_{a,k}
\right).
$$

Define

$$
a_{\mathrm{PC},a,k}
=
\exp\!\left(
-\frac{\Delta t_k}{\tau_{\mathrm{PC},a}}
\right),
\qquad
\tau_{\mathrm{PC},a}>0.
$$

The scalar-ZOH writer is

$$
Z_{4,a,k+1}
=
a_{\mathrm{PC},a,k}Z_{4,a,k}
+
\bigl(
1-a_{\mathrm{PC},a,k}
\bigr)S_{a,k},
$$

with $S_{a,k}$ held over the beat. It is the exact zero-order-hold step of

$$
\tau_{\mathrm{PC},a}
\frac{dZ_{4,a}}{dt}
=
-Z_{4,a}+S_a
$$

for that held source. This is the accepted family-local completion, not a unique RC temporalization.

> **Primary source object:** `REAL-PC`.

> **Equation/contract rows:** `D10.2-EC-PARENT-REAL-PC`, `D10.2-EC-PC-WRITER-COEFFICIENT`, `D10.2-EC-PC-ZOH-WRITER`.

> **Associated accepted profile claim:** `D10-CL-O-006`.

#### 10.5.1 Bounded carrier domain

Declare

$$
\mathcal B_{R,a}
=
\left\{
Z:
\lVert Z\rVert_K\leq R_a
\right\},
$$

and

$$
m_a(R_a)
=
\sup_{
X\in K_{X,a},
\,Z\in\mathcal B_{R,a}
}
\left\|
S_a(X,Z)
\right\|_K.
$$

The exact carrier-domain admission criterion is

$$
m_a(R_a)
\leq
R_a,
$$

together with

$$
H_{\mathrm{profile}}
\left(
K_{4,\mathrm{base}}
+
\mathcal B_{R,a}
\right)
\subseteq
\mathcal H_{\mathrm{adm}},
$$

and regularity of the candidate current solve throughout the declared state/carrier chart.

For nonnegative step duration,

$$
0\leq a_{\mathrm{PC}}\leq 1.
$$

On the primary positive-duration profile,

$$
0<a_{\mathrm{PC}}<1.
$$

When the source and carrier remain in the convex carrier ball, the writer stays in the ball without clipping, projection, post-hoc normalization, or append-only history. The accepted theorem is local and parametric; it does not instantiate universal numerical radii or margins.

#### 10.5.2 Formation, persistence, release, and matched forcing

From neutral state,

$$
Z_{4,a,k}=0,
\qquad
S_{a,k}\neq 0
\quad\Longrightarrow\quad
Z_{4,a,k+1}
=
\bigl(
1-a_{\mathrm{PC},a,k}
\bigr)S_{a,k}
\neq 0.
$$

With zero source,

$$
S_{a,k}=0
\quad\Longrightarrow\quad
Z_{4,a,k+1}
=
a_{\mathrm{PC},a,k}Z_{4,a,k}.
$$

For variable positive step durations and zero source,

$$
Z_{4,a,n}
=
\exp\!\left(
-\sum_{k<n}
\frac{\Delta t_k}{\tau_{\mathrm{PC},a}}
\right)
Z_{4,a,0}.
$$

This gives finite-time persistence and asymptotic native release. It is not a finite threshold event or administrative reset.

Under matched future forcing, the accepted carrier-difference bound contracts by the declared coefficient plus source Lipschitz contribution when the preregistered total is strictly below one. This is a carrier-state contraction result. It does not by itself establish nonzero endpoint hysteresis in $C$, current, geometry, or any downstream observable.

> **Equation/contract rows:** `D10.2-EC-PC-RELEASE`, `D10.2-EC-PC-MATCHED-FORCING`.

#### 10.5.3 Candidate states and lifecycle

The PC complete candidate states are:

$$
X_{A,\mathrm{PC},k}
=
\bigl(
C_k,W_{A,k},Z_{4,A,k}
\bigr),
$$

$$
X_{C,\mathrm{PC},k}
=
\bigl(
C_k,Z_{4,C,k}
\bigr),
$$

with $T_C$ still derived in the C profile.

Snapshot, reset, migration, topology-event, and loss semantics must bind $Z_4$ explicitly. A same-carrier-space context change may transport the carrier only through its declared map. A carrier-space or topology event must use a typed structural map, reinitialize or archive with an information-loss receipt, or fail closed. Generic array resizing is not a history map.

PC is not Candidate B. It is one admitted realization-local independent structural state, crossed with A or C. Its existence does not prove that coherence-only Markov closure universally fails or that every GRC-v4 profile requires explicit history state.

> **Associated negative boundary:** `D10-CL-X-005`.

### 10.6 Coupled Implicit plus Persistent Carrier — CI+PC

CI+PC combines:

```text
same-beat coupled current/geometry closure
+
prior committed K_4 history.
```

It does not reopen a general combinatorial search over all realization pairs. The accepted hybrid pressures only CI+PC for A and C.

The complete states are

$$
X_{A,\mathrm{CI+PC},k}
=
\bigl(
C_k,W_{A,k},Z_{4,A,k}
\bigr),
$$

$$
X_{C,\mathrm{CI+PC},k}
=
\bigl(
C_k,Z_{4,C,k}
\bigr),
$$

with $T_C$ derived. The joint unknown remains

$$
Y_a
=
(J_a,h_a).
$$

The current primary profile freezes

$$
\rho_{\mathrm{inst},a}=1,
$$

while

$$
\rho_{\mathrm{inst},a}=0
$$

is the PC ablation. $\rho_{\mathrm{inst}}$ is profile metadata, not runtime tuning state.

> **Primary source objects:** `REAL-CI-PC`, `SPEC-COMPOSITION-PROFILE-IDENTITY`.

> **Equation/contract parent rows:** `D10.2-EC-PARENT-REAL-CI-PC`, `D10.2-EC-PARENT-SPEC-COMPOSITION-PROFILE-IDENTITY`.

> **Associated accepted profile claims:** `D10-CL-O-007`, `D10-CL-N-008`.

#### 10.6.1 Composition law

For A,

$$
K_{\mathrm{eff},A}
=
K_{4,\mathrm{base}}
+
Z_{4,A,k}
+
\rho_{\mathrm{inst},A}
S_A(J_A,h_A).
$$

For C,

$$
K_{\mathrm{eff},C}
=
K_{4,\mathrm{base}}
+
Z_{4,C,k}
+
\rho_{\mathrm{inst},C}
S_C(J_C,h_C).
$$

The geometry equation is

$$
F_{h,a}
=
h_a
-
H_{\mathrm{profile}}\!\left(
K_{\mathrm{eff},a},
h_{4,\mathrm{ref}},
U_k
\right)
=
0.
$$

$F_{J,a}=0$ is the accepted candidate-specific CI current equation evaluated at the same trial geometry. $Z_{4,a,k}$ is a committed input to the root, not a root unknown.

> **Equation/contract rows:** `D10.2-EC-CI-PC-A-COMPOSITION`, `D10.2-EC-CI-PC-C-COMPOSITION`.

#### 10.6.2 A and C joint roots

For A, the root contains the full A-CI residual from §10.2.1 together with

$$
F_{h,A}
=
h_A
-
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
Z_{4,A,k}
+
\rho_{\mathrm{inst},A}
S_A(J_A,h_A),
h_{4,\mathrm{ref}},
U_k
\right)
=
0.
$$

It uses the accepted bounded composite self-map and contraction conditions. $\widehat W_A(h)$ is recomputed within each root evaluation.

For C, the root contains the full once-gated C-CI residual from §10.2.2 together with

$$
F_{h,C}
=
h_C
-
H_{\mathrm{profile}}\!\left(
K_{4,\mathrm{base}}
+
Z_{4,C,k}
+
\rho_{\mathrm{inst},C}
S_C(J_C,h_C),
h_{4,\mathrm{ref}},
U_k
\right)
=
0.
$$

The accepted result is a contraction on the declared fixed-selector stratum and closed carrier ball. Exactly one self-consistent regular root on the preregistered local branch is admitted; multiple, disconnected, singular, or nonfinite roots fail closed.

> **Equation/contract rows:** `D10.2-EC-CI-PC-A-ROOT`, `D10.2-EC-CI-PC-C-CONTRACTION`, `D10.2-EC-CI-PC-C-ROOT-SELECTION`.

#### 10.6.3 One source, two temporal consequences

After a valid root $(J_a^\star,h_a^\star)$, the carrier writer is

$$
Z_{4,a,k+1}
=
a_{\mathrm{PC},a,k}Z_{4,a,k}
+
\bigl(
1-a_{\mathrm{PC},a,k}
\bigr)
S_a(J_a^\star,h_a^\star).
$$

The same root source $S_a(J_a^\star,h_a^\star)$ must be used:

1. immediately in $K_{\mathrm{eff},a}$ through $\rho_{\mathrm{inst},a}$; and
2. prospectively in the carrier writer.

Using one source to close the root and another to write history would create an unregistered split profile.

The exact gain audit is:

```text
chi_a:
  once in the accepted causal read path

zeta_a:
  once in S_a = Delta K4_a

rho_inst,a:
  once on the immediate source in K_eff

kappa_H:
  once when H_profile consumes K_eff

a_PC,a:
  once in the post-root carrier writer
```

The writer does not reapply $\rho_{\mathrm{inst}}$, $\zeta$, or $\chi$. New $Z_{4,a,k+1}$ is never read in the same beat.

For a constant source $S$ with $0<a_{\mathrm{PC}}<1$, the carrier tends to $S$, so

$$
K_{\mathrm{eff}}
\longrightarrow
K_{4,\mathrm{base}}
+
\bigl(
1+\rho_{\mathrm{inst}}
\bigr)S.
$$

For the accepted primary $\rho_{\mathrm{inst}}=1$ profile,

$$
K_{\mathrm{eff}}
\longrightarrow
K_{4,\mathrm{base}}+2S.
$$

This gain-two result is a declared profile property, not an error and not amplitude equivalence with CI or PC. A normalized or differently weighted hybrid would be a new complete profile.

#### 10.6.4 Exact ablations

The accepted ablations are:

```text
rho_inst = 0 with PC enabled
  -> PC

Z_4,k = 0 with PC disabled and rho_inst = 1
  -> CI

rho_inst = 0 with PC disabled and Z_4,k = 0
  -> fixed-reference transition
```

These are profile reductions, not evidence that the enabled hybrid is equivalent in amplitude, timing, or state authority to its ablations.

> **Equation/contract row:** `D10.2-EC-CI-PC-ABLATIONS`.

#### 10.6.5 CI+PC claim ceiling

CI+PC establishes a bounded local hybrid for A and C with one immediate and one retained structural path. It does not establish:

- that all realization pairs compose;
- OS+PC or RG+PC profiles;
- a unique or preferred immediate/history weighting;
- amplitude-neutral comparison with CI or PC;
- global root uniqueness;
- structural or temporal stability;
- nonzero endpoint hysteresis;
- a universal persistent-carrier ontology.

### 10.7 Comparative disposition

The accepted realization synthesis does not rank the five families. It identifies distinct causal and state commitments.

| Realization | Accepted defining feature | Authoritative realization history | Accepted local defect or boundary | What is not claimed |
|---|---|---|---|---|
| CI | simultaneous current/geometry root | none merely by CI | local regular branch only | global uniqueness or stability |
| OS | one predictor, one geometry update, one corrector | none | explicit geometry fixed-point residual | equivalence to CI or iterative convergence |
| RG2b | lagged deterministic invariant section | no serialized geometry | uniqueness relative to frozen Lipschitz extension | universal reconstruction, $C^1$ section, spectrum |
| PC | scalar-ZOH persistent $K_4$ carrier | $Z_{4,a}$ | local bounded carrier domain | universal memory law or endpoint hysteresis |
| CI+PC | simultaneous root plus prior committed $K_4$ history | $Z_{4,a}$ | local hybrid branch and gain-two profile | preferred weighting or exhaustive composition |

The families answer different questions. A result about current/geometry timing cannot be used as evidence for independent history authority; a persistent carrier cannot be used as evidence that a simultaneous root is necessary; local reconstructibility cannot be used as a distinct temporal family unless it changes the accepted state or timing semantics.

No “best realization” follows from the accepted equations. A preference claim requires a named comparison objective, matched units and capacities, matched steady amplitudes where relevant, and evidence suited to that objective.

### 10.8 Sections 8–10 claim ceiling

Sections 8–10 establish, for the current initial population:

- the complete accepted A candidate-local recurrence;
- the complete accepted C candidate-local selected-sector/Hodge recurrence;
- exact candidate authority and derived-state boundaries;
- exact once-gated A and C Read-Back placement;
- typed A and C structural sources;
- the CI joint-root profiles for A and C;
- the one-pass OS profiles for A and C;
- the bounded RG2b invariant-section profiles for A and C;
- the scalar-ZOH PC profiles for A and C;
- the gain-two CI+PC profiles for A and C;
- profile-local regularity, failure, state, and history boundaries;
- the no-ranking comparative disposition.

They do not establish:

- runtime implementation or conformance;
- runtime-reached formation, retention, release, replay, or migration;
- physical nonabsorbability of A or C;
- nonzero committed endpoint effects;
- structural or temporal stability;
- numeric continuation spectra;
- universal physical units or cross-profile magnitude equivalence;
- global roots or branches;
- a preferred candidate or realization;
- future-exhaustive constitutive or realization taxonomies.

> **Associated future-exhaustiveness boundary:** `D10-CL-C-012`.

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
| “`D10_2_CL_N_001` is a queryable accepted claim or graph successor node.”   | D10.2 provenance/explorer boundary         | Treat it only as a source-local label under `/claim_topology_effect`; retain `D10-CL-C-011` as the historical conditional node and verify the status update from the exact audit-record fields. |

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
