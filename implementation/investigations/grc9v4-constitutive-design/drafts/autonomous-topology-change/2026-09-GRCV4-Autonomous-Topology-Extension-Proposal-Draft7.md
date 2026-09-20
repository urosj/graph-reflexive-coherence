# Autonomous Topology Continuation in GRCV4 — Draft 7
## A source-grounded constitutive proposal for the claim–debt investigation

**Date:** 17 September 2026  
**Status:** proposed investigation input; not an accepted ATC theory, specification, implementation, or conformance result.  
**Intended receiving investigation:** `graph-reflexive-coherence/implementation/investigations/grc9v4-constitutive-design`, with admission through its existing claim, debt, provenance, and verification machinery.  
**Scope:** GRCV4 after the user-reported completion of Tranche 7. The source inspection recorded here does not independently reverify that completion or the final two commits.  
**Relationship to earlier drafts:** replaces their active argument. Earlier proposals are retained, corrected, decomposed, or explicitly dispositioned below; obsolete drafts are not appended as competing instructions.  
**Authority boundary:** no accepted core paper, GRCV4 contract, historical claim, debt disposition, or side-tool bundle is changed by this document.

---

## Reading this proposal

The question is no longer whether we can imagine a graph that grows, simplifies, changes its relations, or replaces one of its modules. GRCV4 already provides an event boundary through which a declared graph change can be attempted. The question is whether the *present GRCV4 dynamics* can supply that declaration without another agent deciding what the organism ought to become.

This distinction gives the investigation a precise starting point. Ordinary GRCV4 evolution already supplies one partial, profile-specific transition. Its lifecycle already supplies another partial transition for an explicitly declared event. What is missing is the constitutive relation between them: the law that determines whether an event is generated, and, if so, the complete event that is generated.

Draft 7 proposes several answers rather than pretending the first answer is already established. It develops their equations, their consequences, their limitations, and the debts that prevent stronger conclusions. The investigation is then asked to adjudicate *these proposals*, not to invent whatever an unfinished heading might have meant.

The distinction between a proposed construction and an accepted result remains essential. A graph builder can be mathematically complete while its proposed trigger remains scientifically unsupported. A resource map can conserve its exact inputs while a particular numerical representation violates the runtime contract. An event can be lawfully committed without establishing a new identity. These are not reasons to discard the whole construction. They are reasons to split its claims correctly.

The central discipline is therefore:

$$
\boxed{
\text{proposed claim}
\longrightarrow
\text{bearing debt}
\longrightarrow
\text{discriminating pressure}
\longrightarrow
\text{explicit claim transformation}.
}
$$

That is the investigation method inherited from D10, not a new ATC governance system. In particular, an unresolved stronger claim must not erase a weaker construction that has been established, and a passing weaker construction must not discharge the stronger claim's debt. [S08, S09]

### What the document contains

Chapters 1–3 establish the source lineage and the actual mathematical objects available in GRCV4. Chapters 4–6 develop competing event-generation laws, including their causal and symmetry obligations. Chapters 7–9 specify graph, resource, reference, and history construction in enough detail to expose the implementation boundary. Chapters 10–11 address stronger core interpretations and the actual lifecycle composition. Chapters 12–14 make the proposals addressable through claims, debts, pressure cases, and predecessor dispositions.

The tables at the end are an index into the argument. They do not replace it. A reader should be able to understand why a claim matters before consulting its identifier.

### Citation and identifier conventions

References such as **[S05 §13.3]** identify the source and section in the source register. References such as **CL-06**, **DB-04**, **CAN-S**, and **DER-02** are local abbreviations for identifiers prefixed `ATC7-`. They are proposed handles belonging to this draft, not existing identifiers in the admitted side tool. A reference to a real predecessor such as `D10-CL-C-009` retains that predecessor's identity and scope; it does not promote an ATC claim through a similarly named node.

Equations explicitly attributed to a source are inherited only within the source's domain. Equations introduced as candidates or conditional derivations are new proposal content. The accompanying index records those statuses separately. The exact-arithmetic checks supplied with this draft test a small set of mathematical constructions and counterexamples; they are not GRCV4 runtime execution or an ATC conformance campaign.

---

# 1. The source lineage is part of the mathematics

## 1.1 Core, substrate, and extension have different jobs

Core Reflexive Coherence supplies a mathematical account of coherence, induced geometry, retention, continuation, identity, and reorganization. GRCV4 supplies a particular finite-graph realization with explicit state, current, geometry, numerical, and lifecycle contracts. ATC would add constitutive graph-changing behavior to that realization.

Those layers are related, but they are not interchangeable. It would be wrong to require the continuum core to contain the exact algorithm for naming a new graph edge. It would be equally wrong to call an arbitrary graph algorithm an RC topology law because it preserves a scalar budget.

The correct question has two parts. Does the proposed law respect the core meaning claimed for it? Does it operate on the actual state and contracts of GRCV4? The first constrains interpretation and causal structure. The second determines what can be computed and committed. A proposed ATC law must answer both to the extent of the claim it makes.

This is why Draft 7 does not begin with a new universal topology Hessian. GRCV4 already has a structural-analysis construction, a complete temporal-transition construction, and typed graph-event mechanics. We should use those first. Any additional operator, threshold, historical variable, or graph-building rule must then be identified as the new constitutive content it really is. [S03–S07]

## 1.2 The 2025 coherence-only reduction remains relevant, but not every use of its words has the same domain

The 2025 *Reflexive Coherence* paper gives the coherence field and its flux as the primitive mathematical description. Its Appendix Zero also derives an internal graph from spatial coherence basins and time-integrated flux between them. Thus the core does contain a graph construction. What it does not establish is that this derived graph is identical to the finite substrate graph used by GRCV4, or that its signed integrated-flux weights are Candidate A's positive retained weights.

Appendix D defines a particular topology-changing operator, $\mathcal R_{\mathrm{coh}}$, through conservation, support or basin-topology change, viability thresholding, and a post-event restoration condition. Appendix J identifies viability with $-\mathcal P[C]$. Those clauses remain load-bearing when an ATC proposal specifically claims to realize that operator. They do not automatically define every permitted representation transport or every graph event in the GRCV4 lifecycle. [S01, Appendices Zero, D, J]

There are also genuine internal ambiguities in the older presentation. A positive-definite spatial Hessian is described there as a maximum, while the ordinary mathematical convention gives a minimum. The restoration statement combines basin language with a parenthetical local-minimum description. The document also uses “collapse” for extinction in one place. Draft 7 preserves these as source issues. It does not silently repair them and then cite the repair as inherited authority.

## 1.3 The later papers refine particular claims; they are not a blanket replacement order

*Identity, Choice, and Abundance* gives choice as a situation in which compatible finite continuations coexist, and collapse as the resolution event. Its broader abundance narrative proposes a generative tendency. The August *Continuation Spectrum* paper narrows that narrative: structural accessibility is state-dependent, and no general monotonic growth of the basin repertoire follows from the equations developed there. It separates spatial scale, constrained structural curvature, temporal relaxation, spatial critical-point geometry, and finite nonlinear attractors. [S02, S03]

The sign discussion in *The Continuation Spectrum* is especially instructive. It introduces a local density $W$, noting the literal inherited convention $W=-V$, and proceeds conditionally with the chosen density and its derivatives. That gives a usable mathematical convention. It does not license treating all older occurrences of potential, viability, basin, and stability as identical after a global name replacement. Nor does it mean every discrete structural calculation must stop until all historical terminology is repaired.

*Read-Back* adds another decisive distinction. Present activity conditioned by retained structure is not identical to arbitrary present current, and retained structure can harden, soften, rotate, weaken, or be rewritten. The paper does not introduce an additional chooser to actualize finite continuations. None of that proves a particular graph rewrite, but it constrains what ATC may attribute to one. [S04]

The lineage should consequently be recorded clause by clause:

$$
\text{source definition}
\to
\text{later clarification or restriction}
\to
\text{GRCV4 realization}
\to
\text{ATC addition}.
$$

A later sentence matters because of what it establishes, not simply because of its date.

## 1.4 What GRCV4 contributes that ATC must not reinvent

The GRCV4 paper describes the accepted architecture as a common contract, a constitutive family, and a geometry-temporal realization. Its initial population crosses A and C with OS, CI, RG2b, PC, and CI+PC. That is a population of ten family/realization products; a complete executable profile additionally binds its parameters, domains, conventions, references, and numerical policy. A family name is not a universal admission certificate. [S05 §§1–3; S07]

The paper's design status and the implementation's execution status must also remain separate. A design paper can accurately state that it does not itself prove runtime conformance even after a later implementation tranche has been completed. Conversely, a reported implementation completion does not turn every conditional analysis formula into an instantiated numerical result. This draft uses the user-reported Tranche-7 boundary as its target substrate, without claiming an independent rerun of the final captures.

The current event supplements are particularly useful. They distinguish explicitly requested history reconstruction from representation-only transport, define exact affine resource arithmetic, and keep current and reset transformations together. They also state that general topology-changing preservation of W and Z needs separate authority. ATC must generate one of those admitted kinds of request, or propose a successor contract where they are insufficient. It must not change their meaning inside a generator. [S10–S13]

## 1.5 What the source comparison does and does not decide

The sources support retaining several distinctions. Structural softening is not by itself a proof of topology change. Graph surgery is not by itself a proof of spark, identity creation, or extinction. Numerical certification failure is not by itself a physical instability. Causal authority cannot enter through a cache, observer, or untyped scheduler.

They do not uniquely prescribe an event generator. They also do not establish a universal prohibition on numerical search, simultaneous events, constitutive thresholds, or every provisional graph change. Those are questions about the declared causal law and the claim being made. A numerical procedure that evaluates one fixed constitutive relation is different from an undeclared policy that chooses a preferred outcome.

**CL-01 — scoped inheritance.** The proposal is to preserve these source distinctions while admitting new graph-changing constitutive choices only as named successors. This is an architectural claim about the ATC investigation input, not a claim that any candidate below is already the RC law of topology. Its bearing debt is **DB-01**, source and implementation-baseline admission. Failure to pin an execution subject blocks runtime attribution; it does not erase the mathematical proposal.

---

# 2. The organism ATC actually acts on

## 2.1 State, publication, and permitted causal input

Let $\mathcal G=(V,E,\partial)$ be the finite oriented multigraph. Parallel edges have distinct identities. Each edge has a tail and a head, and a loop has two endpoint roles even though both roles name the same vertex. Write $B$ for incidence and $d_0=B^\top$.

For a complete profile $p$, the current dynamic authority has one of four forms:

$$
 x_p=C,\qquad (C,W_A),\qquad (C,Z_{4,C}),\qquad (C,W_A,Z_{4,A}).
$$

Only C is resource. W and Z, when present, are nonresource causal state. Candidate C's selected sector, retained Hodge, resolvent and read surfaces are reconstructed; they are not additional free coordinates merely because they carry historical dependence. The reference package contains the graph-bound pairings, candidate reference data, structural base, differential recipe, context contract, and complete-profile identity. [S05 §§3–10; S07]

The lifecycle publication is larger than $x_p$. Denote it here by

$$
 s=(\mathcal G,p,R,U,x_p,x_{p,\mathrm{reset}},Q_*,t,k,\mathcal L),
$$

where $R$ is the reconstructible reference package and $\mathcal L$ is the admitted receipt/archive state. This is explanatory notation, not a replacement serialized schema.

A generator should not automatically read every field merely because the lifecycle stores it. Its *causal input projection* must be declared. The initial candidates in this draft use

$$
 \sigma(s)=(\mathcal G,p,R,U,x_p,t)
$$

only where time or context is already a declared physical input. Reset and charge target participate in full event admission, but do not rank physical event candidates under these initial laws. Receipt hashes identify evidence; they do not decide where to split. A successor that uses reset, previous events, or an explicit memory of unsuccessful probes must say so and justify that historical dependence.

This is a new ATC design choice, not a claim that all legitimate future generators must ignore every lifecycle field. It supplies a clean control: two publications differing only by a zero-duration administrative receipt must have the same physical generator result under these candidates.

## 2.2 The ordinary map and event map are already different owners

Write the accepted ordinary transition as the partial map

$$
 \Phi_{p,\Delta t}:s\rightharpoonup s_1.
$$

It reconstructs or solves the selected profile, consumes one authoritative current in one continuity update, performs the appropriate writers, checks postconditions, and commits or rejects. It does not become an ATC transition merely because a diagnostic is returned.

Write the existing event application as

$$
 \operatorname{Apply}_{\mathrm{evt}}(s,e)\rightharpoonup s^+.
$$

The event preimage e includes the target graph and reference package, the resource transform, history policies, lineage and other contract-required inputs. It is not just an operation name such as “merge.” A complete generator must ultimately determine every semantic field that the caller would otherwise have supplied. Hashes and receipts are then built and validated by their existing owners.

**CL-02 — generator factorization.** ATC proposes a new partial constitutive generator

$$
 \operatorname{Gen}_{\theta,p}(\sigma(s))\in
 \{\mathrm{no\ event}\}\cup\mathcal E(s),
$$

with separately represented unresolved or uncertified outcomes. The governing parameter $\theta$ binds the actual law, not an external chooser's preferences. A useful factorization is

$$
 \operatorname{Gen}_{\theta,p}
 =\operatorname{Build}_{\theta,p}
 \circ\operatorname{Resolve}_{\theta,p}
 \circ\operatorname{Analyze}_{\theta,p}.
$$

The factorization is an organizational proposal. It does not prove an endogenous generator, and it need not survive as three separate runtime components. **DB-02** attaches to its causal-input and trigger completeness, not to the already existing event executor.

### Physical prescription and wire binding are distinct

In the generator notation, e first denotes a *physical event prescription*: the graph map, resource rule, reference construction and history policies resolved from the permitted causal input. The full wire request must additionally bind the actual source identity, both lifecycle roles and the appropriate archive fields. Write

$$
 e_{\mathrm{wire}}=\operatorname{Bind}(s,e_{\mathrm{phys}}),
 \qquad
 s^+=\operatorname{Apply}_{\mathrm{evt}}(s,e_{\mathrm{wire}}).
$$

This binding is deterministic construction from the real publication, not a second physical decision. Changing an excluded receipt head or reset state can change the request's identity and even make full target admission fail; it must not change which physical locus the initial generator resolves. The distinction is necessary because a content-addressed wire event cannot be a function of a causal projection that deliberately excludes some of its provenance fields.

An ATC-enabled complete profile should be understood as a successor $\bar p=(p,\theta)$, with the entire new causal law identity-bound. This draft does not silently attach mutable generator parameters to an unchanged GRCV4 profile identity. A topology event reconstructs the graph-bound target profile and preserves or explicitly transforms $\theta$ according to its declared successor contract.


## 2.3 The current reconstructed now is not the current consumed before

Suppose an ordinary step used $J_k$, wrote $C_{k+1}$, and, for A or a persistent realization, wrote W or Z. Reconstructing a current from the committed poststate generally yields a different current from $J_k$. Both may be useful, but they answer different questions.

The first proposal here, **CAN-STAGE-NOW**, reads the current reconstructed from the present committed state under a declared state-readmission recipe. For OS, its basic read is the reference-geometry state current. An optional read-only OS-pass witness uses a newly reconstructed predictor/corrector pass from that same present state, with its prescribed parameters and no continuity or writer commit. For CI and CI+PC it is a fresh admitted root; for PC it is the read through present retained Z; for RG2b it is the reconstructed section and native current on the state-admission domain.

The alternative **CAN-STAGE-PAST** uses the current actually consumed in the preceding ordinary beat. It may better represent recent activity, but it introduces a causal past operand. A diagnostic receipt that omits the complete current preimage does not make that current reconstructible. This alternative therefore carries **DB-03**, temporal-stage and historical-input closure.

The two proposals can predict different resource split ratios after an A or Z writer changes the poststate. That is a useful discriminator, not noise. The investigation should compare them as different constitutive laws instead of silently switching between whichever current happens to be cached.

## 2.4 Ten products, not ten invented ontologies

The constitutive and temporal factors can be shared where their equations permit. A's full conductance uses its declared differential and baseline. C's current includes its selected-sector and Hodge chain. The realization says when geometry is reconstructed, solved, or retained.

The following table states the inherited obligations that every ATC candidate must respect. It does not assert that the proposed generator already works in every cell.

| Complete family | Present causal authority | Relevant present reconstruction | Additional ATC burden |
|---|---|---|---|
| A_OS | C, W | reference read; optional fresh one-pass OS witness | a split defect is not an alpha mode; keep incoming W fixed during each read |
| C_OS | C | reference read; optional fresh OS witness with both C chains | selector-path validity and current stage cannot be omitted |
| A_CI | C, W | coupled J,h root | structural C-variation fixes W; full temporal variation does not |
| C_CI | C | coupled root including selector/Hodge/baseline dependence | no independent selected-sector perturbation |
| A_RG2b | C, W | invariant section and native current | Lipschitz-only section gives no automatic classical Hessian |
| C_RG2b | C | section plus C reconstruction | section and selector restrictions are separate |
| A_PC | C, W, Z | geometry from present Z, then candidate read | a W or Z memory coordinate does not thereby own a structural spectrum |
| C_PC | C, Z | geometry from present Z and full C chain | current C and retained structure must both remain in the causal preimage |
| A_CI_PC | C, W, Z | coupled root with fixed old Z and immediate source | include both histories without double-counting the source |
| C_CI_PC | C, Z | coupled root with old Z and full selector chain | standalone CI or PC evidence does not close the composition |

For the persistent profiles, the source computed at the selected current and the effective structural input used by the root are distinct. Under CI+PC the latter includes old Z plus the immediate source; the later Z writer must still consume the source once. Any ATC witness or event map that conflates the two changes the existing law. [S05 §10; S07; S14]

**CL-03 — profile-correct reuse.** Candidate-local and realization-local calculations may be reused only with their stage, domain, state and derivative contracts intact. Coverage means an explicit disposition for all ten products, not ten mandatory positive examples under one convenient fixture. A missing RG2b derivative, for example, blocks a derivative-dependent claim through **DB-05**; it does not block a derivative-free current or geometry proposal.

## 2.5 Analysis-only status is not permission to add a new actuator silently

The normative specification says analysis objects do not write runtime state. ATC cannot evade that boundary by placing an existing Hessian in an observer, reading its eigenvalue, and allowing that observer to mutate the graph.

It can propose a successor constitutive law that *consumes* a deterministically reconstructed quantity as an input to an event generator. That is a genuine authority change: the quantity remains derived, but its value now affects physical evolution through a newly declared consumer. The successor must identify that consumer, its stage, profile identity, error policy and claim lineage. A valid structural-analysis interface does not by itself authorize this new use. [S07, Analysis interfaces; S09]

This is the exact meaning of **DB-04**, analysis-to-constitutive consumption. It is not a demand to rederive the existing structural operator. It is the debt incurred when ATC promotes its use from a diagnostic to a causal event guard.

---

# 3. The mathematical analysis we already have

## 3.1 Begin with the constrained structural object, not a convenient matrix

On an admitted smooth structural chart, GRCV4 writes a reduced constrained functional through the profile's geometry relation. In notation chosen here to avoid confusing the constraint multiplier with mobility, let

$$
 \mathscr F_p^{\mathrm{red}}(C)
 =\mathscr L_p(C,h_p(C)),
 \qquad
 \mathscr L_p(C,h)=P_{\mathrm{struct},p}(C,h)-\lambda_Q(Q_\varpi(C)-Q_0).
$$

The current discrete charge law has fixed $\varpi$, so $D_hQ_\varpi=0$. A different geometry-dependent quadrature belongs to a separately declared successor. This is an important instance of substrate specificity: the continuum measure discussion does not authorize ATC to change the existing graph resource law. [S05 §13.3; S07]

The second variation has the full chain

$$
\begin{aligned}
D^2\mathscr F_p^{\mathrm{red}}[u,v]
={}&D^2_{CC}\mathscr L_p[u,v]
 +D^2_{Ch}\mathscr L_p[u,Dh_p[v]]
 +D^2_{hC}\mathscr L_p[Dh_p[u],v]\\
 &+D^2_{hh}\mathscr L_p[Dh_p[u],Dh_p[v]]
 +D_h\mathscr L_p[D^2h_p[u,v]].
\end{aligned}
$$

This is not a decoration around a fixed-graph Laplacian. It is where reflexive dependence of geometry enters the structural calculation. Omitting the last term, or replacing the whole expression with the Hessian of the baseline scalar potential, changes the object being claimed.

One source-backed contribution is

$$
 P_G(C,H)=\frac{\kappa_C}{2}(d_0C)^\top H(d_0C)
       +\sum_i(H_0)_{ii}W_{\mathrm{pot}}(C_i).
$$

At a reference $C_*$, put $e_*=d_0C_*$. Its field contribution includes

$$
\begin{aligned}
\mathscr Q_G[u,v]={}&\kappa_C(d_0u)^\top H_*(d_0v)
 +u^\top H_0\operatorname{Diag}(W_{\mathrm{pot}}''(C_*))v\\
 &+\kappa_C(d_0u)^\top H'[v]e_*
 +\kappa_C(d_0v)^\top H'[u]e_*
 +\frac{\kappa_C}{2}e_*^\top H''[u,v]e_* .
\end{aligned}
$$

The source calls this a contribution, not the whole structural functional under every possible boundary or context. Draft 7 retains that limit. A candidate that needs the complete form must instantiate the remaining declared terms rather than call the displayed expression universally complete. [S05 §13.3.1]

## 3.2 The tangent changes the meaning of zero

Let Z now denote a basis of the admissible structural tangent; this basis symbol is unrelated to the persistent carrier $Z_4$. After removing or classifying protected, gauge and symmetry nulls, a chart representation has the generalized eigenproblem

$$
 Z^\top K_p Z\,\xi_n
 =\alpha_n Z^\top H_0Z\,\xi_n.
$$

Here $K_p$ represents the complete structural bilinear form, not runtime $K_4$. The tangent includes the actual charge constraint and all active boundary restrictions. At a nonnegativity boundary or constitutive kink, a tangent cone or another nonsmooth construction may replace a linear tangent space. An undefined derivative is not a zero eigenvalue. [S05 §13.3.2]

The elementary one-edge matrix

$$
 K=\begin{pmatrix}1&-1\\-1&1\end{pmatrix}
$$

has the constant null vector $(1,1)$. But the unit-charge tangent is spanned by $(1,-1)$, where the Rayleigh quotient is 2. Thus a raw null eigenvalue does not identify a marginal admissible continuation. **DER-01** records this exact counterexample; it is a logical discriminator for a proposed analyzer, not a native GRCV4 result.

The same discipline applies to the earlier pressure candidate $P=ID\chi$. It can be retained as a proposed scalar derived from a properly instantiated form, but it cannot first invent a Hessian and then inherit the meaning of $\alpha$ from notation. **DB-06** covers the functional, tangent, normalization and metric. **DB-07** covers the additional inference from that diagnostic to a topology-generating law.

## 3.3 A's structural and temporal coordinates are deliberately different

For Candidate A, the accepted structural chart varies C while holding $W_A$ fixed. That does not mean W is causally unimportant. It means that the existing structural functional does not yet supply a joint structural theory in $(C,W_A)$.

The reference contrast still changes during C-variation because $\widehat W_A$ depends on C and on the slaved current/geometry. Setting $\delta W_A=0$ does not set $\delta(W_A-\widehat W_A)=0$. The full chain remains necessary. By contrast, a temporal Jacobian of the committed A step does include variations of W and its writer. These are different perturbation questions. [S05 §§13.3.3, 13.4.1]

For Candidate C, the selected sector is derived. Its first variation includes

$$
 \delta T_C=P_M\delta C+
 \bigl(D_CP_M[\delta C]+D_hP_M[\delta h]\bigr)C_*.
$$

Its higher variations include the selector and geometry chains. Giving $T_C$ an independent perturbation would define a different candidate. An ATC law that consumes C structural evidence must retain this dependence, including the retained-Hodge contribution to the baseline current. [S05 §13.3.4]

For PC and CI+PC, the existence of an additional runtime Z coordinate does not automatically establish a joint structural Hessian in $(C,W,Z)$. One proposed structural analysis can hold the retained coordinates fixed while varying C, but its compatibility with the selected realization must be established. A proposed joint-history structural theory carries a stronger and different debt. The scope of **DB-06** must say which claim is asking for which object.

## 3.4 Root derivatives are available conditionally, and only conditionally

For a regular coupled branch, write

$$
 F_p(Y;X)=0,\qquad Y=(J,h),\qquad B_p=D_YF_p.
$$

When $B_p$ is invertible,

$$
 DY_p[u]=-B_p^{-1}D_XF_p[u].
$$

On a declared $C^2$ chart,

$$
\begin{aligned}
D^2Y_p[u,v]=-B_p^{-1}\bigl(&F_{XX}[u,v]
 +F_{XY}[u,DY_p[v]]\\
 &+F_{YX}[DY_p[u],v]
 +F_{YY}[DY_p[u],DY_p[v]]\bigr).
\end{aligned}
$$

The notation $B_p$ here is a root block, not incidence. For A, the smooth conductance chart and floor behavior matter. For C, selector rank and gap matter. A root solver returning a value does not establish these derivatives. Conversely, a failure of a conservative numerical certificate does not prove a physical singularity. [S05 §13.2.1]

RG2b is the important counterpoint. Its accepted invariant section is Lipschitz-only. Draft 7 therefore supplies derivative-free candidates below instead of forcing a classical section Hessian into every profile. The accepted debt `GTRS-RG-DEBT-C1-SECTION-REGULARITY` is relevant lineage: a bounded Lipschitz result can survive while a stronger differentiability claim remains unearned. [S08; S09]

## 3.5 Temporal stability cannot be borrowed from a structural sign

The complete-step derivative, when admitted, is

$$
 M_p=D_X\Phi^{\mathrm{step}}_{p,\Delta t}.
$$

Its eigenvalues are step multipliers. A rate $-\log\mu/\Delta t$ requires a clock and logarithm convention; it is not the definition of every temporal mode. Candidate A's temporal state includes W, and persistent profiles add Z. Their metrics and cross-block scales must be declared before nonnormality or cross-profile magnitude comparisons are meaningful. [S05 §§13.4–13.7]

The simple system $F(y)=y^2/2$ has positive Hessian, yet the discrete update $y^+=(1-\Delta t)y$ is unstable at $\Delta t=3$. This is **DER-02**. It does not accuse GRCV4 of using that step; it prevents an invalid inference from positive curvature to temporal stability.

The proposal follows from the distinction. Structural witnesses, temporal witnesses, read-back derivatives, spatial operators and numerical certificates may all be useful. They must retain their separate claims. A small OS defect may indicate a good split approximation. A persistent Z may encode history. A low structural eigenvalue may identify accessibility. None becomes the others through a shared field named `pressure`.

## 3.6 What it means to ground a new witness

A witness grounded in this chapter has an exact input domain, a specified existing operator or reconstruction, and an explicitly new interpretation. For example, a constrained negative mode can be mathematically valid while the claim that it licenses binary refinement remains open. That is useful partial progress.

**CL-04 — conditional structural witness.** On a declared smooth branch with its complete form, admissible tangent, metric and protected null treatment, a separated constrained mode can serve as a derived ATC input. It does not itself prove graph inadequacy, select a locus, or license a graph event. Its dependencies are **DB-04–DB-08**. Accepting its analysis construction would not discharge those downstream debts.

---

# 4. One constitutive generator, several possible factorizations

## 4.1 A useful formal target

Let $\mathcal E(s)$ be the set of complete event preimages compatible with the source identity. The generator proposed here is not a free search over that set. A finite policy $\theta$ supplies its graph templates, guards, metrics, reference constructors, history choices and numerical recipes before an event is evaluated.

A useful general form is a relation

$$
 \mathcal R_{\theta,p}(\sigma(s),e)=0,
 \qquad
 \mathcal G_{\theta,p}(\sigma(s),e)\ge0,
$$

where the first part specifies equations and the second admissibility guards. An implementation may compute a unique physical event class, report that no guard is active, or report unresolved multiplicity or insufficient certification. These outcomes should not be collapsed into the same scientific assertion.

For a first executable candidate, a single-valued partial form is simpler:

$$
 \operatorname{Gen}_{\theta,p}(\sigma(s))=
 \begin{cases}
  e_* & \text{one event class is constitutively resolved},\\
  \varnothing & \text{the law has no active event},\\
  \mathrm{unresolved} & \text{the declared law does not distinguish alternatives},\\
  \mathrm{uncertified} & \text{the available numerical evidence is insufficient}.
 \end{cases}
$$

The distinction is not a demand for four new persistent states. It is a proposed result type. In all non-event outcomes, the source remains unchanged. An internal programming error is an exception, not another value pretending to describe physics.

## 4.2 Why explicit thresholds are not automatically choosers

Every constitutive completion chooses a response relation. A threshold can be part of such a relation. The scientific issue is whether its inputs, value, units, timing, and interpretation have been declared and justified, not whether the source code contains a comparison.

Likewise, a numerical root iteration can evaluate a fixed constitutive equation without becoming another agent. The no-additional-chooser constraint should prevent an untracked preference from deciding the outcome. It should not prohibit all computation that contains branching.

Draft 7 therefore separates two cases. Solving the declared event relation, refining an enclosure, or proving a target certificate evaluates a fixed claim. Trying unrelated future trajectories, selecting the preferred one, and calling that preference already-existing RC dynamics introduces additional authority. Such a search could itself be proposed as a new constitutive model, but its state, objective, horizon and causal role would need their own investigation. It is not inherited by the current proposals. [S02; S04; S07]

This also changes how failed target admission is handled. The initial candidates below do not choose a runner-up after failure. That is an explicit constitutive policy, **CAN-RES-U**, because it makes event resolution independent of incidental target-search order. An alternative law whose defining relation includes target feasibility must make that dependence explicit and prove its outcome independent of enumeration. No blanket claim that “search is an oracle” is needed.

## 4.3 The causal projection controls what can influence the event

Under the initial projection $\sigma$, changing an audit label, adding a telemetry record, or inserting a successful zero-duration observation cannot alter the physical event. Changing W, Z, context, or the actual current state can alter it because those quantities are already causal inputs.

A refractory mechanism is different. Even if the number of previous physical events can be reconstructed from receipts, using that number changes the generator's causal dependence. Reconstructibility is necessary for replay, but it is not a scientific justification. A refractory proposal therefore either enlarges $\sigma$ with a declared history-derived coordinate or introduces explicit ATC memory with reset, migration and serialization rules. It carries **DB-22**, rather than being smuggled into an implementation scheduler.

This is **CL-25 — explicit historical causation**. It preserves the useful episode idea without treating all stored history as automatically legitimate dynamics.

## 4.4 Physical equivariance, not accidental determinism

Let g denote an admitted relabeling and signed edge-coordinate action. The physical event output should satisfy

$$
 [\operatorname{Gen}_{\theta,gp}(g\sigma)]
 =g[\operatorname{Gen}_{\theta,p}(\sigma)],
$$

where brackets denote the event's physical correspondence class, not byte equality of coordinate-sensitive IDs. References, backend inputs, metrics and target profiles must transform along with the state.

If $g\sigma=\sigma$, this implies

$$
 g[e_*]=[e_*].
$$

**DER-03** is the immediate proof: substitute the invariant source into equivariance. It excludes an arbitrary choice of one exchanged locus, but it does not imply that no event is always the only answer. An unordered symmetric split, an invariant batch, or no event can all satisfy the equation if their constructions are admitted.

**CL-08 — equivariant event classes.** This is a conditional mathematical requirement for the deterministic candidates, not a claim that existing floating-point implementations satisfy exact equivariance in every regime. Its implementation debt is **DB-10**. Near a threshold, algebraically equivalent computation orders can change rounded decisions. A candidate must specify outward comparison, exact arithmetic, a robust guard margin, or an honest numerical limitation.

## 4.5 No universal inference from a small margin

Suppose an implementation returns `uncertified` because its iteration budget ended. That does not mean structural marginality. Suppose a constrained mode is negative. That does not mean the current graph must change. Suppose a target graph admits. That does not mean the organism generated it autonomously.

The generator must therefore contain an explicit new law between available evidence and the event. A transparent but unproven law is preferable to a hidden one. The next chapter supplies several concrete candidates and states exactly where their scientific interpretation remains unearned.

---

# 5. Competing proposals for what generates a topology event

## 5.1 CAN-S: a structural-mode refinement law

The first proposal retains the most developed idea from the earlier drafts but gives it a narrower and more exact meaning. It does not assert that softening forces topology change. It proposes a particular hybrid law that couples a qualified structural condition to a specified refinement.

Assume the state is associated with a declared smooth structural chart and reference branch from Chapter 3. Fix a positive metric normalization, a separation margin $\delta_{\mathrm{gap}}$, a negativity margin $\delta_\alpha$, a local participation threshold $m_0$, and a partition margin $\delta_q$. All are identity-bearing candidate parameters with units, not constants chosen after a favorable run.

The source must first meet the branch and state-association conditions. An exact critical state is one possible initial domain. A larger tubular neighborhood requires a defined projection or chart association and a bound on the difference between its reference spectrum and the actual state. That extension is not supplied merely by calling the current state “near a basin.” It belongs to **DB-05** and **DB-06**.

Let u be a simple separated structural mode with

$$
 u^\top H_0u=1,\qquad
 \alpha_1< -\delta_\alpha,\qquad
 \alpha_2-\alpha_1>\delta_{\mathrm{gap}}.
$$

For a candidate source vertex v and each incident half-edge h attached to an edge e, define

$$
 q_{v,h}=u_{\operatorname{other}(h)}-u_v,
 \qquad
 m_v=\sum_{h\in\delta_H(v)}w_e^{\mathrm{ref}}q_{v,h}^{\,2}.
$$

This lift uses scalar vertex-mode coordinates, not signed physical flux coordinates. Edge-coordinate reversal therefore does not change $q_{v,h}$. Replacing u by $-u$ exchanges the two sign blocks but preserves the unordered partition and $m_v$.

The binary lift is defined only when every relevant $|q_{v,h}|>\delta_q$, both signs occur, and $m_v>m_0$. It partitions the incident half-edges by the sign of q. A loop has $q=0$ under this simple lift, so this candidate cannot resolve a partition at a vertex carrying such a loop. That is a real domain restriction of CAN-S, not a statement that the graph builder cannot handle loops. A stronger half-edge witness is developed below as an alternative.

A homogeneous score can be

$$
 z_v=\frac{m_v}{m_0}
       \frac{-\alpha_1-\delta_\alpha}{a_0},
$$

with $a_0>0$ a declared stiffness scale. CAN-RES-U selects a unique eligible locus only under a declared gap between its score and competitors. It then invokes the binary builder and a chosen resource/reference/history policy.

This gives a concrete conditional generator. Its outputs are not unspecified. Its debt is the *reason for the coupling*: why should this negative mode and sign partition resolve a graph refinement rather than ordinary fixed-graph reorganization? That is **DB-07**, and it bears directly on the claim that CAN-S is an RC-consistent formation law. Mathematical validity of the mode and covariance of the partition do not discharge it.

**CL-04** supports the upstream witness. **CL-09** addresses resolution. **CL-11** addresses the builder. Their separation permits the investigation to retain two of them even if the third fails.

### A retained alternative: the original susceptibility product

The earlier product $P=ID\chi$ remains **CAN-S0**, not discarded history. Once g, H and M are defined from an admitted structural chart, one may set

$$
 I=\left[1-\frac{\|g\|_{M^{-1}}}{\varepsilon_g}\right]_+,
 \qquad
 D=\left[\frac{\varepsilon_\alpha-\alpha_1}{\varepsilon_\alpha}\right]_+,
 \qquad P=ID\chi.
$$

This has a different onset from CAN-S: a still-positive but sufficiently soft mode can produce positive P. It also suppresses large first-order drift. These are constitutive choices, not deductions from the core's vocabulary. The finite comparison must include a state that is soft but restores on the same graph. If CAN-S0 would mutate it while CAN-S would not, the difference is substantive and should be retained in the claim transformation.

A capacity gate $\chi$ is optional. Generic GRCV4 has no universal degree cap, so $\chi=1$ is the neutral candidate. A GRC9 saturation gate is a specialization with its own source. An unmotivated generic degree threshold would be a new mechanical model, not inherited capacity.

## 5.2 CAN-L: a half-edge lift with no arbitrary eigenvector sign

A more general lift can start from a local symmetric half-edge interaction form $A_v$ derived from a precisely declared graph quantity. One candidate is the restriction of a graph-structural bilinear surface after removing signed-coordinate dependence by a justified correspondence to endpoint variables. Another is a response-derived form. Neither construction is automatic: **DB-08** requires the actual map and covariance proof.

Once such a form exists, the combinatorial law can be complete. For every nontrivial unordered bipartition $\pi=\{H_0,H_1\}$ of the finite incident half-edge set, define

$$
 \mathcal J_v(\pi)
 =\sum_{h\in H_0,\ell\in H_1}a_{h\ell}
   +\tau_b\bigl(|H_0|-|H_1|\bigr)^2.
$$

The parameter $\tau_b$ and the meaning/sign of $a_{h\ell}$ belong to this new candidate law. The optimizer is not being attributed to the core. It is an explicitly proposed finite constitutive partition rule. A unique minimizer modulo block exchange, separated by a declared margin, supplies the partition; otherwise the result is unresolved. Exhaustive evaluation is finite, with $2^{d-1}-1$ possible unordered partitions for d half-edges. A practical implementation requires an explicit work bound or an exact equivalent algorithm. Exceeding that bound is computational noncertification, not absence of physical pressure.

This proposal makes a useful distinction about “no chooser.” A static, fully specified minimization can be a candidate constitutive law, just as another implicit equation can be. It becomes scientifically acceptable only if the investigation admits its objective, inputs and interpretation. It is not acceptable merely because the minimizer is unique. The causal-dependence claim remains under **DB-02**, **DB-04**, **DB-07**, and **DB-28**.

Unlike CAN-S's simple neighbor-mode signs, CAN-L can in principle assign the two ends of a loop differently. It can also retain an unresolved symmetric partition. The two lifts should compete where both are defined; they should not be silently combined when one fails.

## 5.3 CAN-Q: coarsening from a present-state quotient relation

A different proposal begins from over-representation rather than structural instability. Let T aggregate a proposed source block into a coarser resource vector. Let L be a declared lift with

$$
 TL=I.
$$

For an adjacent pair under unit resource measure, T sums the pair and L may distribute the aggregate equally. The relation $C= LTC$ then says the fine resource lies on the proposed lifted coarse subspace. It does not say the complete organism is equivalent to a coarse one: W, Z, references and currents may still distinguish the vertices.

Let $f_p(x)=-B J_p(x)$ be the present resource tendency reconstructed at the selected stage. A bounded resource-only witness is

$$
 r_C=\|C-LTC\|_{H_0},
 \qquad
 r_f=\|f_p(x)-LTf_p(x)\|_{H_0}.
$$

The initial guard requires $r_C\le\varepsilon_C$ and $r_f\le\varepsilon_f$, with a declared graph block and reference metric. This is a completely evaluable present-state condition wherever the current is available. It has no need for a classical RG2b section derivative.

Its weakness is equally explicit. Two fine states can have the same T C and different W or Z that alter later current. Even with identical W/Z now, equality of a tendency at one point does not establish invariant quotient dynamics. Consequently the proposed event may be a *state-conditioned lossy coarsening*, but it cannot yet be called an exact behavioral quotient.

The stronger claim uses a complete state map H and target dynamics satisfying

$$
 H\Phi_-(x)=\Phi_+(Hx)
$$

on a declared invariant source domain. Here H includes every causal coordinate and reference/history interpretation, not only T C. This intertwining relation would make coarse evolution a genuine quotient on that domain. Whether it holds for any nontrivial GRCV4 pair is an open, concrete claim, **CL-06**, with **DB-25** as its central debt.

There is also a useful approximate theorem. Suppose

$$
 \|H\Phi_-(x)-\Phi_+(Hx)\|\le\varepsilon
$$

uniformly on the domain, and $\Phi_+$ is L-Lipschitz on the corresponding target trajectories. With target initial state $y_0=Hx_0$, the discrepancy obeys

$$
 e_{n+1}\le L e_n+\varepsilon,
 \qquad
 e_n\le\varepsilon\sum_{j=0}^{n-1}L^j.
$$

This is **DER-04**. It follows by adding and subtracting $\Phi_+(Hx_n)$, then applying the two bounds. It is a prospective certificate for a fixed declared map, not a comparison of several imagined futures followed by a preferred selection. Domain invariance, H's full-state meaning, and the uniform bound remain bearing debts. A finite collection of matching trajectories does not prove them.

The event builder can still be investigated without that stronger theorem. A lossy merge, a behaviorally approximate quotient, and an exact quotient are three different claims. They must not receive one combined “coarsening passed” label.

## 5.4 CAN-R+: a missing-relation proposal from present geometry

A graph can encode effective coupling beyond its explicit adjacency. This suggests a candidate for edge birth that uses a present, reconstructed GRCV4 object rather than inventing a field on absent edges.

Let H be the declared positive one-form Hodge at the chosen present read. Define

$$
 K_V=BHB^\top.
$$

For two distinct nonadjacent vertices a,b with positive diagonal terms, define

$$
 q_{ab}=\frac{|(K_V)_{ab}|}
 {\sqrt{(K_V)_{aa}(K_V)_{bb}}}.
$$

Because $K_V$ is positive semidefinite, $0\le q_{ab}\le1$. A zero diagonal leaves this candidate undefined at that pair; it is not repaired by a small denominator. Under an admitted action $B'=PBU^\top$, $H'=UHU^\top$, the node form transforms as $K_V'=PK_VP^\top$. Thus q is permutation-covariant and does not depend on edge orientation. These are conditional algebraic results, **DER-05**.

The candidate constitutive guard is $q_{ab}>\theta_{\mathrm{birth}}$, accompanied by an explicitly declared nonadjacency rule and a unique resolved pair or invariant batch. The builder then creates the specified relation with its own target reference policy. The rule is new. q measures a particular present geometric coupling, not proof that an explicit new edge is necessary, nor proof that Candidate A or C consumes that coupling nontrivially.

A three-vertex path illustrates the mechanism without overclaiming. With

$$
 B=\begin{pmatrix}1&0\\-1&1\\0&-1\end{pmatrix},
 \qquad H=\begin{pmatrix}1&1/4\\1/4&1\end{pmatrix},
$$

vertices 1 and 3 are not adjacent but $(K_V)_{13}=-1/4$, so $q_{13}=1/4$. With diagonal H, this coupling vanishes. The proposal therefore distinguishes a structure-mediated relation from adjacency itself. It still needs **DB-27**, the justification for converting that relation into an edge, and **DB-07**, causal discrimination under candidate consumers and controls.

**CL-05 — geometry-conditioned relation witness.** The algebraic q construction and its covariance are conditional derived claims; the event-trigger interpretation remains a new constitutive proposal under DB-27. This proposal is useful precisely because it is derivative-free. It may be available on RG2b states whose section is only Lipschitz. That does not establish all-ten support; it gives a different dependency path than CAN-S.

## 5.5 CAN-R−: relation deletion requires more than zero current

For deletion, a present current threshold alone is too weak. A bridge edge can have zero current at a symmetric resource state while remaining indispensable to later communication. A positive retained W or a nontrivial Z row can also matter when the present current vanishes.

One candidate therefore combines a declared inactivity measure with a structural redundancy test. On a connected reference graph, choose positive scalar reference weights w and define

$$
 L_w=B\operatorname{Diag}(w)B^\top,
 \qquad
 \ell_e=w_e b_e^\top L_w^+b_e,
$$

where $b_e$ is the incidence column and $L_w^+$ acts on the mean-zero subspace. This is a newly proposed deletion diagnostic, not an identification of reference mobility with generated geometry. A bridge has $\ell_e=1$; a non-bridge can have $\ell_e<1$. Loops require a separate declared handling because their incidence column vanishes.

The bound has a simple linear-algebra basis. Put $A=B\operatorname{Diag}(\sqrt w)$. Then $A^\top(AA^\top)^+A$ is the orthogonal projection onto the row space of A, and $\ell_e$ is its e-th diagonal entry. Hence $0\le\ell_e\le1$. For a bridge, a potential constant on each component after removing the edge can be scaled so that $A^\top z$ is the e-th coordinate vector, giving $\ell_e=1$. For a non-bridge there is a cycle-space vector with a nonzero e component, so that coordinate vector is not entirely in the row space and $\ell_e<1$. A loop has zero incidence and leverage zero; that does not make its W/Z or structural role irrelevant. This proof concerns the chosen reference incidence diagnostic, not the full GRCV4 current or geometry.

A candidate guard can require $\ell_e\le1-\delta_\ell$, small present physical and read-back activity under declared scales, and, for persistent states, a sufficiently small relevant carrier row/column measure. If W history is to be discarded regardless of value, the history policy must say so. Smallness is not a preservation theorem.

This guard is only an operational candidate. It can still delete a relation that becomes important later. A stronger claim of controlled behavioral change needs a bound analogous to the quotient defect, or another explicit target-response estimate on a fixed domain. The debt is **DB-27**, not “all deletion impossible.” The deletion builder itself remains a separate claim.

## 5.6 CAN-V: a viability-conditioned pruning law

The core provides a more specific interpretation for pruning: a viability condition activates removal or redistribution of a coherence basin or subunit. To instantiate that interpretation on GRCV4, the proposal must supply a locus correspondence and a defined functional, not merely rename charge or current regularity as viability.

Take an explicitly selected structural functional $\mathscr P_{p,L}$ on a declared locus and boundary convention, a reference state $x_{0,L}$, a positive scale $s_L$, and a threshold $\theta_L$. A normalized candidate is

$$
 v_L(x)=-\frac{\mathscr P_{p,L}(x)-\mathscr P_{p,L}(x_{0,L})}{s_L}.
$$

Its guard is $v_L<\theta_L$, or an explicitly stated threshold-crossing law. The latter requires a prior value or another causal construction; it cannot be inferred from a single under-threshold snapshot. The distinction is **DB-03** and **DB-18**.

The subtraction removes an additive functional constant within this comparison. It does not prove that the normalization is the core viability, that different graph sizes are comparable, or that the locus is an organismal basin. Those remain **DB-17** and **DB-18**. If the generator is claimed only as a new energy-conditioned graph law, its weaker meaning should be named accordingly. If it is claimed as Appendix-D pruning, the full source correspondence and target restoration obligations attach.

**CL-07 — functional-guarded pruning proposal.** The stated guard is an evaluable law once its functional and locus are supplied; its core viability meaning is not thereby proved. The event produced by this candidate can redistribute the removed locus's C to a declared neighborhood or replacement block. The numerical construction is given later. No resource is deleted merely because a viability score was low.

## 5.7 What has been proposed, rather than delegated

The chapter supplies concrete candidate computations: a constrained-mode lift, a finite half-edge partition law, a quotient-mismatch coarsening law, a geometry-mediated relation-birth law, a redundancy-qualified deletion law, and a normalized functional guard. Each has explicit inputs and conditions. Each also states what the formula does not prove.

The investigation can now reject a particular guard, show that two guards coincide on a restricted domain, or accept a bounded event-generation model while refusing a stronger core interpretation. It does not need to invent an unspecified “topology pressure” before meaningful pressure can begin.

---

# 6. How a witness becomes one event without another agent

## 6.1 CAN-RES-U: unique resolution within one declared candidate family

The simplest candidate does not pretend that a spectral refinement score and a viability score share a universal scale. The complete ATC policy first identifies one enabled witness family, with its own units and comparison rule. The source then determines the finite eligible set. Within that family, an event is resolved only if a unique physical candidate satisfies a declared dominance margin.

For scalar scores z with interval enclosures $[\underline z_i,\overline z_i]$, a robust numerical version requires

$$
 \underline z_i>\theta,
 \qquad
 \underline z_i-\max_{j\ne i}\overline z_j>\delta.
$$

A singleton set needs only the activation condition unless the policy explicitly requires an additional margin over a neutral baseline. The earlier convention of inventing a runner-up score zero is not mandatory and is not silently retained.

If the inequalities cannot be certified, the result is unresolved or uncertified as appropriate. The output must not depend on iteration order or the first candidate encountered. If a candidate is resolved and its built event later fails admission, this policy returns a failed event attempt without promoting a runner-up. That failure behavior is part of CAN-RES-U, not a theorem that every possible constitutive model must behave identically.

**CL-09 — bounded unique resolution.** Given a finite candidate set, invariant scores, certified comparisons and unique dominance, this law determines an equivariant event class. The proof is direct: the source action permutes candidates and preserves their comparison relations, so it carries the unique dominant candidate to the unique dominant candidate. **DB-09** covers score comparability; **DB-10** covers numerical certification; **DB-02** covers why this comparison is the proposed constitutive law rather than an already inherited one.

## 6.2 CAN-RES-X: several families with explicit exclusivity

A richer policy can enable several witness families but avoid inventing a common score. Let $G_\omega(s)$ indicate that family $\omega$ has a resolved local witness under its own law. One candidate global rule is

$$
 \sum_\omega \mathbf1_{G_\omega(s)}=1.
$$

If exactly one family is active, its event is attempted. If more than one is active, the result is unresolved. This law is conservative and may suppress many events, but it has a precise interpretation. It does not silently prefer refinement to coarsening.

An alternative binds a partial order $\succ_s$ between typed witnesses. That relation must be defined by equations or explicit physical criteria, not by names of operation families. For example, a proven exact quotient certificate might be incomparable with a structural-instability refinement witness until a common compatibility relation is supplied. The existence of two numbers is not proof that comparing them is meaningful.

The investigation should test CAN-RES-X against a declared priority model rather than rule out priority in advance. A priority model can be a new constitutive proposal, but its fixed ordering is then genuine new authority and must be challenged as such. **DB-09** is local to those mixed-family claims. It is not required by a one-family generator.

## 6.3 CAN-RES-B: compatible events as one invariant batch

Exact symmetry can support a batch even when it forbids a single distinguished locus. Suppose the source has two exchanged regions and the law produces an event at each. The set can be symmetry-invariant even though neither element is invariant individually.

The hard part is not naming the set. It is proving that a simultaneous event has a complete meaning. Let $e_1,e_2$ have disjoint resource loci. Their resource transforms may commute, but target profiles, references and histories can still interact. In particular, the current reconstruction policy can reinitialize all W or all Z after each event. Two individually local edits can therefore have globally different consequences when applied sequentially.

A sufficient factorization would require all shared data to agree, the combined graph construction to be unambiguous, the resource maps to commute on both roles, and the complete history/reference maps to satisfy the corresponding commuting relation. Only then can one compare sequential composition with the batch. If those equalities fail, the batch can still be defined as its own atomic event, but it is not equivalent to the sequence.

**CL-10 — invariant batch possibility.** Symmetry does not prohibit a scientifically defined simultaneous event. Its construction and equivalence claims carry **DB-11**, which requires complete critical-pair analysis rather than disjoint node names. This preserves the useful alternative without pretending that batch execution is already supported by Tranche 7.

## 6.4 Event identity is downstream of physical resolution

After a physical event class is resolved, deterministic names are needed. A source identity, the full typed locus/partition preimage, the new policy identity and role labels can generate child and edge identifiers. Collisions must reject or be handled by an explicitly declared injective naming scheme. Truncating a hash and silently choosing another available name is not a scientific resolution law.

The order of two unordered child blocks can be canonicalized for serialization. That does not create a physical left and right. The resource shares, backend positions, edge incidences and signed tensor actions must follow the same block correspondence. Reversing the serialization order must exchange the representation, not change which physical child receives more resource.

Names can depend on a recorded event nonce only as labels after physical resolution, provided changing that nonce leaves the physical transition equivalent. They cannot decide a tie. This gives a direct pressure case: vary only content labels or receipt heads while holding $\sigma(s)$ fixed. The predicted graph transition must remain the same up to its admitted correspondence.

## 6.5 Hysteresis and refractory periods are separate proposals

The earlier refractory rule is retained as **CAN-MEM**, but no longer treated as harmless orchestration. An explicit candidate memory state is

$$
 a_{k+1}=\begin{cases}0&\text{after a successful topology event},\\a_k+1&\text{after a successful positive ordinary beat},\\a_k&\text{otherwise}.
 \end{cases}
$$

An event guard may require $a_k\ge N_{\mathrm{ref}}$. The counter's overflow, reset, rebase, migration, duplicate, representation and event semantics must be specified. It is either a declared causal coordinate or a specified causal projection of a ledger whose required event information is actually retained. Merely counting all receipts is wrong because receipt groups and zero-duration operations are not physical beats.

A state-only alternative uses hysteresis in actual witness values. Birth can require $q>\theta_{\mathrm{on}}$, while deletion requires $q<\theta_{\mathrm{off}}$, with $\theta_{\mathrm{off}}<\theta_{\mathrm{on}}$. This avoids a hidden timer but does not by itself rule out oscillation, since the graph event changes q's domain and references. The two proposals therefore have different debts. Neither is accepted as a generic cure for endless graph churn.

---

# 7. Graph construction: complete mechanics without premature physical meaning

## 7.1 The construction tuple

Once a witness is resolved, the builder must determine a finite target. A useful proposed record is

$$
 e=(\mathcal G^-,\mathcal G^+,L^-,L^+,\beta_\partial,
 \Lambda_V,\Lambda_E,T,b,R^+,p^+,U^+,\mathcal H_W,\mathcal H_Z).
$$

The loci $L^\pm$ identify the edited regions. $\beta_\partial$ describes external attachment correspondence. $\Lambda_V,\Lambda_E$ record lineage. T and b define the resource map. The target reference, complete profile and context must be actual preimages. History policies are fixed before reconstruction.

This is **CAN-GRAMMAR**, not a replacement for existing request schemas. Some fields already live in the graph/event preimage; some may be derived evidence; any genuinely new field needs successor admission. The tuple is useful only insofar as it exposes the information a complete endogenous law must supply.

A source locus can be small while its trigger depends on the wider organism. GRCV4 distinguishes graph-local assembly from the support of inverse operators and full causal response. ATC should not turn local graph surgery into an unsupported local-causation theorem. [S05 §§1.2, 6]

## 7.2 CAN-BIN: binary vertex refinement on a multigraph

Let $\delta_H(v)$ contain the endpoint roles of all edges incident to v. A loop contributes two elements, $(e,\mathrm{tail})$ and $(e,\mathrm{head})$. The resolved witness supplies an unordered partition

$$
 \delta_H(v)=H_0\dot\cup H_1,
 \qquad H_0\ne\varnothing,\quad H_1\ne\varnothing.
$$

Replace v by children $v_0,v_1$. For each old edge endpoint h at v, replace that endpoint with $v_i$ exactly when $h\in H_i$. Preserve every old edge identity and its tail/head role. Add a new internal edge $e_*$ between the two children with a declared coordinate orientation.

This closes the loop ambiguity. A loop whose two ends lie in the same block remains a loop on that child. A loop whose ends lie in different blocks becomes an old edge between the children. It remains distinct from the newly added internal edge, so parallel child edges are allowed. No edge is duplicated or lost. Unaffected endpoints remain unchanged.

**DER-06 — graph validity.** Each old edge has exactly two endpoint roles before the operation. The endpoint substitution maps each role to exactly one valid target vertex. Therefore every old edge still has exactly two valid endpoints. The target has $|V|+1$ vertices and $|E|+1$ edges, provided fresh names are distinct. This proof uses the half-edge partition, not an assumption that the graph is simple.

**CL-11 — binary builder.** CAN-BIN is a graph-generic combinatorial construction within the finite oriented multigraph type. It does not prove that any analyzer generates its partition, that target references admit, or that children are identities. Those are **DB-08**, **DB-12**, **DB-14**, **DB-16**, and **DB-26**, respectively attached to the stronger assembled claims.

The graph operation is covariant if the source action carries the half-edge partition and child roles with it. CAN-S is only one restricted way to generate that partition. CAN-L is another. Failure of CAN-S at loops does not invalidate the builder's loop handling.

## 7.3 CAN-MERGE: forward coarsening without an archived parent

Choose an unordered source block S, initially an adjacent pair $\{u,v\}$. Replace S by w through a vertex quotient map $\pi_V$. The simplest complete edge policy is to preserve every old edge identity and map both endpoints through $\pi_V$. Every internal edge becomes a loop at w; external parallel edges remain parallel.

This is **CAN-MERGE-KEEP**. It reduces vertex count without automatically reducing edge count. That may be a useful coarsening, but it is not equivalent to deleting every internal relation.

A second policy, **CAN-MERGE-DROP**, explicitly removes a declared subset of edges whose endpoints both lie in S. The witness may select all internal edges, one designated connecting edge, or another fully specified subset. Its event history must name the removed edge lineages and their history loss. It cannot quietly collapse parallel edges into one because they share target endpoints.

The two policies produce different graphs, history maps and target references. A single word “merge” is not a sufficient event preimage. **CL-12** covers each specified quotient construction; **CL-06** addresses the much stronger assertion that the quotient preserves behavior. **DB-25** must not block the weaker combinatorial result.

Unlike reversion, neither policy requires the source vertices to descend from a previous split. Its endogenous trigger comes from a current-state law such as CAN-Q or CAN-V. The proposed trigger, rather than the graph shape, distinguishes coherent coarsening from viability-conditioned pruning.

## 7.4 CAN-EDGE and CAN-REWIRE: relations with explicit lineage

An edge-birth template preserves V and inserts one fresh edge between the resolved endpoints. Its eligibility predicate states whether parallel edges and loops may be born; no implicit simple-graph assumption is allowed. The first missing-relation candidate CAN-R+ restricts itself to distinct nonadjacent vertices. A more general multiplicity law would be a different candidate.

An edge-death template removes exactly the resolved edge identity. It does not aggregate resources automatically because vertex coordinates remain unchanged. History and reference restrictions still apply, and deletion of the last edge can fall outside the current complete-reference schema even when the graph operation is well-defined abstractly. The correct result is unsupported target admission, not a dummy edge.

A rewiring template preserves an edge identity but changes one or both endpoint roles according to the resolved witness. This explicitly claims relation lineage. An alternative death-plus-birth template uses a new edge identity. Even if their final incidence matrices agree, their lineage and history assertions differ.

**CL-13 — relation and local-replacement construction.** These templates are complete graph operations once their endpoint and lineage data are resolved. Their stronger physical meaning remains under **DB-27**. The proposal does not identify every edge death with extinction or every edge birth with a new enduring relation.

## 7.5 CAN-BIRTH and CAN-DEATH: resource must have somewhere to go

Pure vertex birth can be made combinatorially complete by a finite template: insert one new vertex, connect it to the resolved boundary ports, and supply a target reference constructor. There are at least two distinct resource policies. A zero-resource birth extends C with zero. A redistribution birth takes a declared dyadic fraction from a resolved source block. The first changes representational capacity without creating resource; the second changes both topology and its placement. Neither is automatically a biological or core-level reproduction event.

For vertex death, the template must specify all incident edge actions and every source resource column. One candidate redirects resource to a resolved surviving neighborhood with nonnegative coefficients summing to one. Another removes a zero-resource vertex under a separately declared resource-map convention. Under the currently inspected exact column-stochastic event policy, even a zero-valued removed coordinate still needs a valid represented column; silently dropping that column is not admitted merely because the current value is zero.

There is a simple impossibility boundary. If the target has no resource coordinates and the event is closed with positive source charge, no linear resource map can satisfy $\varpi_+^\top T=\varpi_-^\top$. With unit positive source weights, the left side has no contribution. Thus total disappearance of positive closed-system resource cannot be represented by this event class. It requires redistribution, an explicitly accounted boundary exchange, or a different model. This is **DER-07**, not a claim that every form of extinction is impossible.

**CL-14** separates finite graph birth/death construction from resource and core interpretation. Its bearing debts are **DB-12–DB-18**, activated according to the particular claim.

## 7.6 CAN-REPLACE: a boundary-preserving module rule that is not an arbitrary search

A replacement law needs an actual source of the target module. “Construct a better module” is not a definition. Two concrete candidates are retained.

The first is **boundary-hub replacement**. A resolved connected source locus S is replaced by one hub w. Every external half-edge keeps its outside endpoint and reattaches its inside endpoint to w. Internal edges are handled by a fixed keep-as-loops or drop policy. T aggregates source C into w. This is a module-sized version of the quotient construction; it is not claimed to preserve all internal behavior.

The second is **boundary-path replacement**. A policy binds a finite target path template and an attachment map determined by the resolved witness. To avoid ID-based physics, the witness must supply the physically distinguished attachment order or an unordered equivalence class for which all admitted representations give the same event. Without such an order, the rule is unresolved. A fixed library of templates can be part of $\theta$, but it is new constitutive context, not something derived from the core by naming it a library.

Both candidates generate one target from the resolved preimage. Neither searches arbitrary graphs until one later performs well. A richer endogenous module synthesis remains a separate candidate with its own equations and debts.

An atomic replacement is not automatically equivalent to deleting S and then inserting the target. The deletion intermediate may be outside the reference or charge domain. It may also discard history that the atomic map transports. **CL-30** therefore requires equivalence of complete maps and admissible intermediates before replacing an atomic event with a sequence. **DB-11**, **DB-15**, and **DB-23** carry that burden.

## 7.7 CAN-REVERT: inverse lineage is not inverse dynamics

The archived split can determine an inverse graph map: merge its two children, remove the specifically created internal edge, and restore each old endpoint role from lineage. That closes the graph ambiguity even after representation relabeling, provided the episode correspondence is transported lawfully and no intervening edit has invalidated the locus.

It does not restore old W or old Z after the children have evolved. It does not reverse the intervening ordinary dynamics. It does not erase the original event's receipts. Current and reset resource are merged according to the chosen current event map; the earlier pre-split arrays are not substituted.

A failed-probe reversion trigger needs causal episode state or reconstructible declared history and an explicit completion criterion. A forward coarsening trigger does not. Their graph outputs may match in a special case without making their scientific events identical.

The purely real split/merge resource composition can be identity on the original coordinate: $(p_0+p_1)C_v=C_v$. Stored binary64 resource need not round-trip, especially at subnormal values. Therefore even an immediate graph inverse does not prove exact scientific-state inversion. The event's actual charge and restoration checks remain authoritative.

## 7.8 Graph mechanics and core interpretation stay on separate axes

The construction chapter has described graph changes. Pruning, extinction, spark, and identity-preserving reorganization describe additional meanings that may attach to some of them. One merge might be a coherent quotient, another a viability-loss response, and another an explicitly lossy administrative reconstruction. The same graph shape does not decide.

**CL-28 — independent interpretation.** The operation catalogue is retained, but its terms are decomposed into mechanical map, lineage policy, endogenous guard, and claimed interpretation. This is more informative than eleven primitive labels and avoids imposing an artificial hierarchy of event “tiers.” Chapter 10 states the additional evidence required by the strongest interpretations.

---

# 8. Resource and reference construction must meet the real numerical contract

## 8.1 The event map is not merely a conservation slogan

For each lifecycle role $r\in\{\mathrm{current},\mathrm{reset}\}$, the inspected event contract evaluates

$$
 C_r^+=\operatorname{RN}_{64}(T C_r^-+b),
$$

with each affine component accumulated exactly from the supplied finite binary64 inputs before one final rounding. In its current closed unit-vertex scope, represented matrix coefficients are nonnegative and every column sums exactly to one. The general paper also retains a charge-covector contract for separately admitted measures. [S05 §12.7; S10]

An endogenous generator must produce a T that actually satisfies the selected numeric policy. It cannot output real-number formulas and assume that independently rounding them will preserve the contract.

This is already exposed by a split with activities 1 and 2. The nearest binary64 values of $1/3$ and $2/3$ add in exact rational arithmetic to

$$
 1-2^{-54},
$$

although their floating sum is 1. The old current-share recipe was therefore incomplete as an implementation proposal. That does not refute current-sensitive splitting. It identifies a specific missing coefficient construction, **DB-13**.

## 8.2 CAN-TDY: an exactly conservative dyadic split

Choose an identity-bearing integer $b_q$ with $1\le b_q\le52$, and set $N=2^{b_q}$. For nonnegative exact activities $L_0,L_1$, define

$$
 r=\begin{cases}
 L_0/(L_0+L_1),&L_0+L_1>0,\\
 1/2,&L_0+L_1=0.
 \end{cases}
$$

Let $k=\operatorname{RoundEven}(Nr)$, and store

$$
 p_0=k/N,\qquad p_1=(N-k)/N.
$$

Both coefficients are exactly representable binary64 values, their exact sum is one, and

$$
 |p_0-r|\le\frac1{2N}.
$$

The same bound applies to the complementary share. Because N is even, nearest-even rounding obeys

$$
 \operatorname{RoundEven}(N-Nr)=N-\operatorname{RoundEven}(Nr).
$$

Consequently exchanging the two activity blocks exchanges $p_0,p_1$, including exact midpoint ties. This is an important advantage over rounding one coefficient and assigning a numerically privileged residual to the other.

These statements are **DER-08**, a conditional arithmetic result for the new candidate. The grid size is new constitutive/numerical policy. Quantizing the resource split can alter event outcomes, so it must be identity-bound and pressured. It is not a silent repair of the old policy.

The activities themselves can be defined as

$$
 L_i=\sum_{h\in H_i}|J_{e(h)}|,
$$

using the selected present-current stage. A loop contributes once for each endpoint role assigned to a child. That convention is explicit: the activities measure half-edge participation for this allocation rule, not net resource crossing a cut. An alternative sums distinct edges per block and treats split loops differently. That alternative needs a different policy identity.

For $L_0=1,L_1=2$ and $b_q=4$, the proposed shares are $5/16$ and $11/16$, not independently rounded thirds. Their accuracy is lower than full binary64 precision, but exact conservation and symmetry are transparent. Increasing $b_q$ reduces the quantization bound without changing the proof. **CL-15** covers this precise result; it does not claim that activity magnitude is the physically correct allocation measure.

## 8.3 Alternatives remain live, but their differences are explicit

**CAN-TEQ** assigns $p_0=p_1=1/2$. It is exactly conservative and symmetric, with no current-stage dependency. It may fail to express differentiated participation. That is a different scientific hypothesis, not merely a low-accuracy CAN-TDY implementation.

**CAN-TCONT** allocates according to a qualified continuation-mode mass, for example the H0-weighted norm assigned to each child region. This may align resource with the mode that generated the split, but it adds a locus-to-child measure and still requires an exactly represented T. The same dyadic construction can implement its final scalar share once that measure is defined.

**CAN-TRAT** keeps exact rational coefficients in a new event schema. It can preserve the real current-share ratio exactly, but it is not executable under a schema that accepts only binary64 coefficients. It therefore carries a contract-successor debt in addition to the scientific allocation debt.

The investigation can compare these proposals on the same resolved split and target profile. It should not choose whichever makes one fixture pass and retrospectively call it the original law.

## 8.4 Exact coefficient conservation does not guarantee exact stored charge conservation

Even CAN-TDY does not make every rounded output preserve the sum exactly. If $C_v=2^{-1074}$ and both shares are one half, each child resource rounds to zero. The exact affine map is conservative; the stored output is not. The lifecycle's actual charge delta and tolerance policy must decide whether the event admits.

This distinction is essential for stronger closed-core claims. The current event contract can track the actual charge change of the rounded target and adjust its recorded target according to its declared policy. A proposal claiming *exactly closed coherence conservation* may need the stronger condition that the actual event delta is zero, not merely that T is column-stochastic. It may instead need a separately admitted balanced-rounding rule. Neither choice can be hidden inside the builder.

Likewise, current and reset are independently mapped using the *same event T and b*. Different roles can have different rounding errors. Both must satisfy the common updated charge target. A reset-only failure rejects the whole event.

**CL-16 — resource accounting.** The proposed construction separates exact map conservation, stored resource, actual charge change and the charge target. A baseline offset between actual charge and an admitted Q target must not be silently repaired. A stronger exact-conservation claim activates **DB-13**; it does not follow from the weaker validity of an affine map.

## 8.5 Coarsening and redistribution maps

A unit-measure quotient has particularly simple exact coefficients: each source column contains a single 1 at its continuing target vertex. This covers a merge that sums the source block and leaves other coordinates unchanged. It is exactly column-stochastic, but final target sums still use the event's round-once arithmetic and admission.

For a pruning or death candidate with several recipients, each removed source column needs a complete probability vector. One candidate allocates on a fixed dyadic grid. Let positive recipient weights $a_1,\ldots,a_m$ be derived from the resolved witness. A symmetric multi-recipient rule is harder than the binary complement rule: assigning the final residual to the last ID introduces an ordering bias. A fully specified candidate can instead use exact quotas and largest-remainder allocation only when all relevant remainders are separated; unresolved ties return no uniquely resolved allocation or an admitted symmetry-invariant allocation class. An alternative uses equal dyadic shares when the recipient count is a power of two.

These are new proposals, not complete universal allocation laws. Their debt is local. Binary refinement can use CAN-TDY without waiting for arbitrary-recipient pruning to be solved. A donor with no admitted recipient cannot disappear in a closed event by omission.

## 8.6 CAN-REF-GM: an exact finite recipe for the new-edge reference seed

The old geometric-mean seed can be made numerically precise without changing its real-valued definition. Let $w_1,\ldots,w_m>0$ be the distinct incident reference-edge weights selected by the policy. Define

$$
 g=\left(\prod_{i=1}^m w_i\right)^{1/m}.
$$

This is the same real geometric mean as an exact log-average/exponential expression. It is bounded by the minimum and maximum source weights, positive, permutation-invariant and homogeneous under positive common scaling. Those are useful properties, but none proves that the mean is the correct RC constructor.

A proposed finite algorithm interprets the source weights as exact dyadic rationals and forms the rational product. It locates the adjacent positive binary64 numbers $a\le g\le b$ by monotone search, comparing $x^m$ with the exact product. It then compares the product with $((a+b)/2)^m$ and selects the nearest endpoint, with ties to even. Exact representable roots return immediately. Because g lies between existing finite positive weights, this result cannot overflow or underflow outside that interval.

The algorithm avoids loss through separately rounded logarithms. It is not claimed to be cheap for arbitrarily large degree: rational bit growth and the finite search budget must be declared. Budget exhaustion is computational noncertification. The candidate does not silently switch to a cheaper numerical mean.

**DER-09** supplies the bounding and rounding argument. **CL-17** covers the finite constructor and reference-lift proposals, with **DB-14** for scientific choice, context, target identity and numerical work bounds.

Two alternatives remain active. An arithmetic mean can also be evaluated exactly before rounding and has different weighting of extreme inputs. A fixed neutral seed can be independent of source scale but then introduces an absolute reference choice. Their downstream dynamics can differ even when all are positive and covariant. The investigation must retain that distinction.

## 8.7 Structural-base lift: preserve the actual proposal, not just its policy name

For CAN-BIN, map each surviving edge coordinate into the target edge space. A proposed target structural base keeps an old-old entry only if its two edges remain star-adjacent after the endpoint substitution. All newly introduced row/column entries begin at zero:

$$
 K^+_{4,\mathrm{base}}[e,f]=
 \begin{cases}
 K^-_{4,\mathrm{base}}[e,f],&e,f\text{ survive and share a target star},\\
 0,&\text{otherwise}.
 \end{cases}
$$

This is **CAN-KMASK**. It restores a construction lost from the later cumulative drafts. Entry masking preserves symmetry and cannot increase the entrywise Frobenius norm of the retained old block. It does not prove preservation of all geometric or dynamic properties. K4 is not interchangeable with an SPD Hodge matrix, and masking entries would not in general preserve positive definiteness of an unrelated matrix. The target geometry must still be reconstructed and admitted under the actual profile.

For a merge, edges may become newly adjacent. CAN-KMASK leaves newly possible entries zero instead of inventing them. For replacement, a new local base can be zero with the outside reference preserved, or supplied by the selected template. Both are explicit reference construction choices. No change to K4_base should be described as lossless history transport merely because K4_base is reference context rather than W or Z.

## 8.8 Candidate A's host-frame backend lift

The minimal split backend sets

$$
 x_{v_0}=x_{v_1}=x_v
$$

and preserves all other host positions. Old reference edge weights survive; the new internal edge receives its declared seed. Dimension and positive ridge are retained, and the full backend and profile identities are recomputed.

This **CAN-XDUP** introduces no spatial direction. It does introduce a new graph relation between coincident host positions. The WLS normal matrix remains

$$
 M_i=\lambda I+\sum_e w_e\,\Delta x_e\Delta x_e^\top\succeq\lambda I,
$$

so the exact local solve is nonsingular when $\lambda>0$, even for the coincident children. That is a conditional algebraic result, not proof that the resulting differential is physically adequate or that all target values fit the numeric domain.

A directional alternative can separate children along a declared host vector. It is not generic without a lawful source of that vector and a covariance proof. An eigenvector in an unrelated analysis coordinate space cannot be treated as a host-space displacement by convenience.

For a merge, a geometric midpoint of the parent host positions is an explicit target-reference candidate. A resource-weighted position is another, but then the reference depends on the current role's resource and must still be one declared common target reference for current and reset. The implementation cannot construct separate incompatible geometries and call them one target profile.

## 8.9 Candidate C reference completion and context lift

Candidate C requires exact live-edge coverage of its fixed reference field. Surviving edges receive the selected transported scalar values; new edges receive the declared seed; removed edges disappear from the map. Its reference Hodge and mobility remain sibling constructors with different roles. Retained Hodge and selected-sector surfaces are rederived, not transplanted from the source.

Context is no less important. A fixed, graph-independent no-flux context may have an identity lift. A node-indexed boundary field or a prescribed external port does not. A birth, merge or replacement must define the target context preimage or reject that context family. “Keep context unchanged” is not meaningful when its coordinate domain changed.

These obligations belong to **DB-14** and **DB-26**. They are why a complete graph builder is necessary but not sufficient for an executable event.

---

# 9. History is not whatever survives in an array

## 9.1 Three independent transformations

An event can preserve resource while changing topology and losing history. It can also change coordinate-sensitive hashes while preserving the represented scientific structure through an exact coordinate action. Therefore three maps must remain distinct:

$$
 \text{topology/lineage},\qquad
 \text{resource},\qquad
 \text{nonresource history}.
$$

This is not merely an ATC philosophical preference. The inspected GRCV4 contracts make candidate and carrier history separate event channels, with their own source commitments and dispositions. [S10, S11]

For a pure representation change with vertex permutation P and signed edge permutation U,

$$
 B^+=PB^-U^\top,\qquad
 C_r^+=PC_r^-,\qquad
 W_{A,r}^+=|U|W_{A,r}^-,\qquad
 Z_r^+=UZ_r^-U^\top.
$$

That action preserves the appropriate represented structure when references and profile inputs transform consistently. It is not a generic topology-changing transport rule. Reusing it after merging edges, deleting coordinates, or creating a new relation would require a new derivation.

## 9.2 CAN-HRESET: a complete but deliberately lossy first event family

One useful initial proposal reuses the already specified reconstruction/loss policy. On an A target it invokes the target-only reference-pass initializer independently for mapped current and reset C. On a C target it leaves W absent and rederives its surfaces. On a persistent target it creates the complete target-sized zero carrier. Source candidate and carrier histories are explicitly lost where the selected policy says so. [S10; S12]

The A initializer's causal order matters:

$$
 C^+\to D(C^+)\to W^{\mathrm{base}}=G_W(C^+,0)
 \to\Phi^{\mathrm{base}}\to J_{\mathrm{ref}}
 \to W_A^{\mathrm{init}}=G_W(C^+,J_{\mathrm{ref}}).
$$

The final conductance retains the full current-dependent channel. The auxiliary conductance is not final retained authority, and the producer does not require a full total-current solve at that auxiliary W merely to obtain its baseline. Final realization-specific target readmission follows. This order is inherited from the selected initializer successor, not invented again by ATC.

**CL-19 — initializer reuse.** A topology generator should construct the target graph, differential and context inputs, then use the admitted producer, not supply a guessed zero flux or a new self-consistent initializer. **DB-16** concerns complete current/reset integration and target failure, not the already selected producer's law.

CAN-HRESET gives an honest first end-to-end candidate, but its scientific cost is substantial. Adding one edge can trigger reinitialization of all W and reset of all Z. An experiment cannot attribute its result to topology alone. It combines topology change, reference change, and active-history removal. A control with the same history reconstruction but identity topology is therefore essential.

## 9.3 CAN-HINJ: a stronger preserving extension should remain a live proposal

A more conservative topology change can have an injective edge map. Consider adding a disconnected zero-resource vertex while leaving every existing edge intact. One candidate keeps old W and Z exactly and defines only the new vertex/reference/backend inputs. That could preserve the old active edge history without a merge rule.

This is not automatically admitted by unchanged array dimensions. The target profile, the additional zero-resource coordinate, C selector behavior, backend reference, reset mapping and full lifecycle still need closure. The point of the candidate is to isolate a tractable preserving case rather than jump directly to arbitrary graph transport.

A general edge map L must satisfy more than a dimensional relation. Even

$$
 B^+L=T_C B^-
$$

does not uniquely determine L, since a cycle-space-valued addition can preserve the equation. Moreover,

$$
 L\operatorname{Diag}(W)L^\top
$$

can be dense and leave Candidate A's positive diagonal mobility type. A carrier pushforward $LZL^*$ requires declared pairings, an actual adjoint, support, norm and target-domain bounds. None follows from the resource map alone. [S10]

**CL-18 — independent history policy.** CAN-HRESET, CAN-HINJ and future typed pushforwards are competing history constructions. **DB-15** blocks preserving claims that lack a map; it does not block an explicitly lossy event. A preserving candidate that fails admission must not silently become CAN-HRESET.

## 9.4 History witnesses and core formation are different claims

Equal target values do not prove preservation. The reconstructed zero carrier may equal the source zero carrier while the selected policy still provides no lineage transport. Conversely, signed reorientation can change array values and hashes while preserving the represented carrier.

Likewise, initialization is not native formation, and event-driven loss is not native release. A later ordinary writer may form or weaken a retained structure, but its attribution needs the corresponding history and dynamics evidence. The topology law should not inherit a formation claim from an initializer's nonzero output. [S05 §§5, 12; S12]

## 9.5 Comparing two paths to the same final graph

Suppose an atomic replacement and a two-step edit reach the same graph. At the real affine resource level, composition has

$$
 T_{21}=T_2T_1,\qquad b_{21}=T_2b_1+b_2.
$$

But the runtime sequence rounds after each event, while the atomic map may round once. Its W initializer and Z policy are nonlinear and stage-dependent. Its references and receipts also differ. Therefore equal final graph shape, and even equal real composite T, do not prove equality of complete GRCV4 transitions.

An equivalence claim must identify the state relation, history relation, numerical recipe and admitted intermediate states. Administrative evidence may intentionally remain different even when represented scientific states agree. **CL-30** retains this distinction without asserting that no operation sequences can ever be equivalent.

---

# 10. Stronger core meanings require their own evidence, not another universal gate

## 10.1 Replace the tier ladder with explicit assertions

The earlier P/G/R/I ladder tried to protect legitimate distinctions, but it also suggested a universal route from graph surgery to core event to identity. The sources do not establish that route. A higher-level reorganization can occur on a fixed substrate graph. A graph edit can preserve the higher-level organization. A temporary graph event may or may not be an acceptable constitutive model; calling it “Tier P” does not settle the question.

Draft 7 therefore records independent assertions:

$$
 \mathsf{Endogenous}(s,e),\qquad
 \mathsf{SubstrateValid}(s,e,s^+),\qquad
 \mathsf{RcohCorrespondence}(s,e,s^+),\qquad
 \mathsf{IdentityClaim}_\nu(s,e,\text{evidence}).
$$

These are proposed claim labels, not new runtime predicates that already exist. The first says a declared constitutive law generated the event. The second says the complete substrate transition admitted. The third asks for a specific correspondence to Appendix D of the 2025 core. The fourth identifies a particular stronger interpretation, such as a new stable continuation, same-identity reorganization, or extinction.

An event can establish the first two while leaving the others unproved. Conversely, a fixed-graph trajectory might support an identity claim without any graph event. The assertions should be related only by actual source and proof dependencies, not by a universal hierarchy.

**CL-20** makes the Appendix-D correspondence a specific stronger claim. **CL-28** keeps graph mechanics and interpretation separate. Neither is permission to silently weaken a requested event after one of its required conditions fails.

## 10.2 What a claim to realize $\mathcal R_{\mathrm{coh}}$ actually owes

The 2025 definition supplies four clauses: conservation, changed support topology or basin count, viability thresholding, and post-event local stability restoration. Draft 7 preserves all four when that precise correspondence is claimed. It does not reduce them to ordinary target admission. [S01, Appendix D]

However, each clause requires a discrete realization. The raw graph's vertex count is not automatically a basin count. A signed integrated-flux graph from Appendix Zero is not automatically Candidate A's positive mobility graph. A finite nonlinear attractor basin is not an infinitesimal continuation mode. These are source distinctions, not merely a choice of notation.

A proposed correspondence package must therefore bind a map from the relevant GRCV4 state and declared dynamics to the core objects it claims to represent. A useful notation is

$$
 \mathfrak B_p(x;\mathcal D,\mathcal M)
$$

for an explicitly defined basin or support construction with domain $\mathcal D$ and interpretation $\mathcal M$. The parameters are not optional decorations. A superlevel-set partition requires a level and connectivity convention. An attractor basin requires dynamics and an attraction meaning. An asymptotic finite attractor repertoire cannot be obtained merely by counting local graph minima.

**DB-17** attaches to this correspondence, including which topology notion changes. It does not block construction of an edge-deletion event that makes no $\mathcal R_{\mathrm{coh}}$ claim.

## 10.3 CAN-VABS and CAN-VREL: two viable proposals for viability, not one renamed scalar

A literal candidate starts from a fully specified discrete functional $\mathscr P_p$ and defines

$$
 V_p^{\mathrm{abs}}(x)=-\mathscr P_p(x).
$$

It then binds the functional's sign, additive origin, units, reference volume or pairing, locus, and threshold. This **CAN-VABS** is closest in form to Appendix J. It is incomplete if any of those choices is omitted.

The reason is exact. If $\mathscr P'_p=\mathscr P_p+b$, then first and second variations are unchanged, but $-\mathscr P'_p<\theta$ can have a different truth value. A derivative-derived current cannot recover that lost absolute normalization. **DER-10** records this counterexample.

The relative candidate already used in CAN-V is

$$
 V_p^{\mathrm{rel}}(x)
 =-\frac{\mathscr P_p(x)-\mathscr P_p(x_0)}{s_p}.
$$

It is invariant under an additive constant. If x and $x_0$ have equal charge, it is also invariant under adding a fixed multiple of that charge to the functional. But it introduces a reference state and scale, and it is not automatically identical to the older absolute viability. Its relation to $V[C]$ must be argued, not asserted.

A third possibility uses a prospective local viability certificate rather than a scalar comparison: an admitted restoring domain, boundary viability condition, and resource constraints jointly establish continued operation. That may be useful, but it would require a new claim explaining how it realizes, modifies, or only partially models the core threshold definition. It must not be called the same V by convenience.

**CL-21 — normalized viability proposal.** These candidates permit conditional work under an explicit convention; they do not require a global editorial repair of every older potential sign first. **DB-18** bears on the exact functional, absolute or relative normalization, cross-graph comparability, threshold direction, and source correspondence.

## 10.4 A threshold crossing is not just an under-threshold value

The core uses threshold language and a pre-event inequality. A discrete model must say whether its guard is a state condition or a crossing condition. These are different hybrid laws.

A state guard triggers whenever $V(x)<\theta$ at an eligible boundary. A crossing guard can require

$$
 V(x_{k-1})\ge\theta,
 \qquad
 V(x_k)<\theta.
$$

The second depends on two physical states. If the generator sees only the current publication, that past value is not free. It requires retained causal memory or an explicitly supplied preceding committed-state pair with a reproducible provenance. A failed numerical attempt or a zero-duration administrative operation must not fabricate a crossing.

An operation-specific pair of thresholds may provide hysteresis. Its sign and direction cannot be inferred from the label “refinement” or “coarsening.” The later core narrows universal gradient amplification; the older Appendix-D viability clause is not confined exclusively to pruning. The investigation must identify each driver on its own domain rather than preassign an active growth driver and a passive death driver by analogy. [S01–S04]

## 10.5 Restoration: basin membership, equilibrium, and formed branch are different propositions

Draft 6.1 changed “lies in a basin” into “lies on a locally restoring formed branch.” That strengthened the source without a proof. Draft 7 withdraws the substitution.

The exact counterexample is

$$
 \dot y=-y,\qquad F(y)=\tfrac12 y^2,\qquad y(0)=\tfrac12.
$$

The initial point lies in the basin of the stable equilibrium 0 because $y(t)=e^{-t}/2\to0$. It is not itself critical: $F'(1/2)=1/2$. Basin membership therefore does not imply equilibrium membership. A formed branch of equilibria is stronger still. **DER-11** records this distinction.

The 2025 parenthetical wording leaves a genuine interpretation problem, and the later papers do not authorize us to choose one resolution silently. Draft 7 accordingly offers two explicit target-certificate claims: **CAN-REST-B**, membership in a certified local basin, and **CAN-REST-E**, an equilibrium or invariant-set certificate plus local attraction. Their correspondence with the intended Appendix-D condition is **DB-19**. An implementation may establish the stronger certificate when possible, but it must state what it actually proves.

## 10.6 CAN-REST-B: a concrete local basin certificate for the complete temporal map

Let $\Psi_+$ be the declared target ordinary transition on the complete causal state, not just C if W or Z are present. Let $x_*$ be a target fixed point, let M be a declared positive metric on the relevant constrained coordinates, and let

$$
 D_r=\{x:\|x-x_*\|_M\le r\}\cap\mathcal D_{\mathrm{admitted}}.
$$

Assume the set is closed, is complete in the chosen metric, and the actual map obeys

$$
 \Psi_+(x_*)=x_*,\qquad
 \Psi_+(D_r)\subseteq D_r,\qquad
 \|\Psi_+(x)-\Psi_+(y)\|_M\le q\|x-y\|_M,
 \quad q<1.
$$

Then every $x^+\in D_r$ converges to $x_*$ under the target ordinary law. The proof is the contraction estimate

$$
 \|\Psi_+^n(x^+)-x_*\|_M\le q^n\|x^+-x_*\|_M.
$$

This is a complete conditional local-basin proposition, **DER-12**. It does not require the proposed poststate to equal the fixed point. It does require the entire relevant state, a metric and a uniform domain, all of which are nontrivial in A and persistent profiles.

A useful sufficient route on a smooth convex chart is a uniform derivative norm $\sup_{D_r}\|D\Psi_+\|_M\le q<1$, together with domain and fixed-point checks. RG2b may instead admit a direct Lipschitz estimate. Neither is automatically supplied by a root-block condition number. In particular, a target RG2b state that is readmissible but outside the next ordinary-step entry domain cannot satisfy this certificate merely because its section was reconstructed.

**CL-22 — qualified restoration certificate.** The conditional contraction or Lyapunov route establishes exactly its stated basin or attracting-set result, without redefining the source. Its bearing debt is DB-19, with DB-23 for numerical realization and DB-20 for stronger identity attribution.

There is also a numerical qualification. A certificate for an ideal real-valued $\Psi_+$ does not immediately certify its rounded implementation $\widehat\Psi_+$. If

$$
 \|\widehat\Psi_+(x)-\Psi_+(x)\|_M\le\eta,
$$

then

$$
 \|\widehat\Psi_+^n(x)-x_*\|_M
 \le q^n\|x-x_*\|_M+\eta\frac{1-q^n}{1-q}.
$$

The bound establishes attraction to an error neighborhood, not exact convergence to $x_*$. For an invariant numerical ball, one needs $q r+\eta\le r$ and the admitted state constraints. Calling that result exact core basin restoration would require a separate approximation claim. **DB-19** and **DB-23** preserve the analytic/numerical boundary.

Finally, the full autonomous system has another map: its generator may fire again. A basin certificate for the *ordinary target map* only proves that map's attraction. To claim attraction under the combined ATC dynamics, the certificate also needs a region in which the generator remains inactive, or a stability argument for the full hybrid map. This prevents post-event certification from quietly disabling the very topology law being investigated.

## 10.7 CAN-REST-L: a Lyapunov route that does not require a joint structural Hessian

Another concrete proposal uses a function $L_+(x)\ge0$ defined on the complete target state and a reference invariant set $\mathcal A$. Suppose a compact sublevel set is forward invariant, L vanishes only on $\mathcal A$, and

$$
 L_+(\Psi_+(x))-L_+(x)\le-c\,d(x,\mathcal A)^2,
 \qquad c>0.
$$

Then summing the inequality bounds $\sum_n d(x_n,\mathcal A)^2$, so the distance tends to zero. Additional conditions are needed for convergence to one point rather than merely to the set. This is **DER-13**, a conditional temporal-restoration argument, not a claim that GRCV4 already possesses the required L.

The advantage is that a temporal Lyapunov candidate can be investigated without pretending the accepted structural C-only functional is already a joint W/Z energy. The disadvantage is the substantial new debt of finding and verifying L for the actual map. It must not be replaced by a convenient positive scalar that happens to decrease in a few examples.

## 10.8 Finite persistence is useful evidence with a smaller claim

A candidate completion monitor can test a declared predicate $P_\omega(x_k)$ for N consecutive successful ordinary beats. For refinement, that predicate might involve distinct child signatures and admitted local behavior. For a merge, it might involve the continuing absence of the former separating relation. For replacement, it might involve a boundary response envelope.

A finite run establishes exactly those observations. It does not prove an asymptotic basin, a new finite attractor, or reflexive closure. The monitor should therefore report a completed finite observation episode, not automatically a “completed spark.” A stronger label attaches only through a separately supported correspondence.

**CL-23 — finite persistence evidence.** This is useful even if CAN-REST-B or CAN-REST-L remain unproved. Its debts concern the predicate, sampling boundary, counter state and interpretation, not the existence of an asymptotic theorem. **DB-20** gates identity or spark claims, while **DB-22** gates a monitor that causally triggers later reversion.

## 10.9 Core interpretation is conditional, not a source of automatic prohibitions

The broad graph catalogue remains compatible as a set of substrate hypotheses. The core's possible nonlinear outcomes motivate investigating both differentiation and simplification. They do not prove that a particular vertex merge is pruning, or that only viability-loss events may coarsen a graph.

If a provisional graph event is proposed, its compatibility is an open claim. If it is advertised as an immediate Appendix-D event, the four clauses apply at that event's defined before/after boundary. If it is advertised only as a lower-level GRCV4 constitutive transition, the proposal must state that weaker meaning and justify its relation to the intended substrate. Neither “all probes are allowed” nor “all probes are forbidden by the core” follows from the material inspected here.

The investigation can therefore accept an event construction, retain an unresolved core interpretation, and reject a premature spark label without contradiction. That is exactly why the claims and debts must be local.

---

# 11. Composition with the lifecycle: the new law must not break the old guarantees

## 11.1 CAN-TIME-AFTER: an ordinary beat followed by one autonomous event boundary

The initial scheduling proposal is explicit. After a successful positive ordinary beat commits $s_1$, the generator evaluates $\sigma(s_1)$ once. If it resolves an event, the existing event lifecycle attempts that event from $s_1$. A failure preserves $s_1$, not the state before the already successful ordinary beat.

This creates two distinct transactions:

$$
 s_0\xrightarrow{\mathrm{ordinary}}s_1,
 \qquad
 s_1\xrightarrow{\mathrm{event}}s_2\ \text{or retained }s_1.
$$

The overall operation report must not say that the ordinary beat failed merely because the optional event did. It should retain the successful ordinary receipt and the separate event result. This is the same stage-provenance discipline already encountered during Tranche 7, now applied to a new composition.

An alternative **CAN-TIME-JOINT** makes the entire macro-operation provisional and commits both together or neither. That is a different atomicity contract and can alter clocks, receipts, and failure behavior. It is not obtained by wrapping two existing methods and hoping they are equivalent. A pre-beat event boundary is another distinct candidate because its witnesses read a different state.

**CL-24 — transactional composition.** CAN-TIME-AFTER preserves the existing ordinary and event owners under a new explicit schedule. CAN-TIME-JOINT carries a stronger successor debt, **DB-21**. Neither schedule is claimed as the uniquely core-derived meaning of autonomy.

## 11.2 Observation cannot secretly become actuation

A read-only call that exposes topology diagnostics must not trigger an event. Otherwise polling frequency becomes a physical parameter. Likewise, loading or duplicating a snapshot must reconstruct state without unexpectedly firing a generator.

The proposed autonomous boundary is therefore part of a declared evolution operation, not a side effect of `compute_observables()`, a notebook display, or an IDE refresh. Diagnostics can display the same derived witness, but only the constitutive evolution owner can consume it into an event.

If multiple clients request the same boundary, the implementation needs ordinary stale-source and transaction checks. Replaying a witness whose source identity has changed must reject. Repeatedly invoking an unchanged no-event boundary should not update hidden counters or change a future result.

## 11.3 State admission remains different from readiness for another beat

An event target is readmitted as a state under its declared realization. This is not always the same as proving that another positive ordinary step can begin or succeed. RG2b's smaller entry chart and wider state/section domain are the concrete example. OS state reconstruction is likewise not identical to executing another full positive-duration pass.

The initial ATC event policy retains state admission as the inherited requirement. A stronger **forward-ready event** can additionally require a proof that a specified next ordinary step is admissible, but that is another claim and must not silently strengthen all topology events. A basin or forward-invariant-domain certificate from Chapter 10 would imply some readiness under its own assumptions.

This distinction prevents the generator from creating an event target that it later refuses to restore merely because it is not eligible for another beat. It also prevents the opposite overclaim: a restorable target is not necessarily a target with indefinite future evolution inside the same chart.

## 11.4 No diagnostic repair of a failed target

The builder fixes the operation and policies before target readmission. If target C becomes negative, a solver block is singular, a carrier bound fails, a reference map is incomplete, or a reset-only charge check fails, the requested event rejects. The event owner must not clip C, enlarge a chart, switch realization, lower a threshold, change the initializer, or replace a preserving history policy by a lossy one to make the result pass.

A different explicitly declared feasibility-solving generator could include some of those choices as variables of its defining relation. But then they must be solved under that relation before publication, with complete identity and evidence. They are not an exception handler's private repair policy.

The same rule applies to stronger interpretation claims. If an event request requires a restoration certificate and that certificate fails, the implementation may not silently publish the graph event without the certificate. A separately enabled weaker event class is a different request, not a fallback interpretation.

## 11.5 Evidence, errors and archive closure

Unexpected internal identity or schema-construction failures must not be converted indiscriminately into scientific `invalid_event` results. Known invalid declarations can be typed semantic failures; a programmer error in constructing a supposedly valid target must propagate while preserving the prior publication. The distinction concerns origin and contract, not just whether an exception derives from `ValueError`.

Every proposed successful publication must also remain admissible under its resulting snapshot release/layout. A new ATC wrapper cannot assume that validating its own new row suffices if an operation changes the archive contract or mixes receipt-group types. Prospective archive validation, repeated scientific-identity commitments, current/reset preimages and parent ownership remain inherited obligations. [S11–S13]

**CL-31 — no regression of lifecycle guarantees.** This is a concrete implementation claim, with **DB-21** and **DB-23**. It does not follow from the generator's mathematical purity alone. The pressure campaign must include mixed ordinary, migration, representation, reconstruction, reset and autonomous-event sequences, not only isolated successful examples.

## 11.6 Event rate, repeated failures and finite work

One event attempt per successful positive ordinary beat gives a finite number of event attempts in any finite number of such beats. It does not prove a finite number of events in finite physical time if requested durations shrink with finite total sum. A non-Zeno physical-time claim needs a positive time-step lower bound, a minimum event interval, or another explicit argument.

Similarly, the generator can repeatedly propose an inadmissible target at successive boundaries. Recording a prior failure and suppressing retries changes its causal law; merely leaving the state unchanged can permit repeated attempts. The policy must say which behavior is intended. A source-keyed computational cache can avoid recomputation only if it reproduces the same result without becoming scientific memory.

A conditional stronger bound is available. If a common bounded-below quantity E never increases during ordinary evolution and every accepted topology event decreases it by at least $\delta>0$, then the number of accepted events is at most

$$
 \left\lfloor\frac{E(s_0)-E_{\min}}{\delta}\right\rfloor.
$$

This is **DER-14**. Its assumptions are not established for generic GRCV4, and an event law minimizing such a quantity would be new constitutive content. The result is retained as a possible proof route, not a hidden optimization objective or global finite-growth theorem.

**CL-26** therefore separates finite computational work per boundary, finite events per discrete run, non-Zeno physical time, and global topology-size bounds. Their debts must not be merged.

## 11.7 Episode transport, reset and reversion

A causal episode needs exact lifecycle semantics. Under a pure representation action, its locus and half-edge lineage transform, while its physical age should not restart merely because coordinates changed. Under reset, the current scientific state changes to the reset baseline while the ledger persists. Keeping the episode, clearing it, or mapping it to a reset episode are different laws.

The initial **CAN-MEM** proposal keeps the event lineage but resets its finite completion counter whenever the predicate's input is discontinuously changed by reset, migration or another interfering event. It does not resurrect pre-event W/Z. This is a concrete candidate, not an inherited rule. A second policy may terminate the episode on any such intervention. Their replay predictions differ and should be tested.

A reversion request must verify that its archived inverse topology is still meaningful after all intervening events. It cannot infer missing ancestry by graph matching. If its locus is no longer valid, the reversion is unavailable or rejects under the declared policy; it must not delete unrelated later structure.

---

# 12. Three assembled proposals that can actually enter the investigation

## 12.1 Why assembly matters

A collection of individually plausible ingredients is not yet a generator. To make the proposal testable, this chapter fixes three composed candidates. Each can fail target admission. That is a defined outcome. What it may not do is leave a partition, reference weight, history treatment, or event timing for a runtime caller to invent.

The proposals are not ranked as better organisms. They answer different scientific questions. Their comparison should be preregistered in terms of precise differences, not whichever produces a visually interesting graph.

## 12.2 CAN-A: derivative-free geometry-conditioned edge birth

CAN-A uses CAN-STAGE-NOW and CAN-R+. Its policy binds a birth threshold $\theta_q$, a separation margin $\delta_q$, the finite arithmetic/enclosure recipe, and the reconstruction/loss history policy. It operates only on distinct nonadjacent vertex pairs with positive diagonal node-form terms. It does not create parallel edges or loops.

At an eligible post-beat boundary, reconstruct the present Hodge and current under the active profile. Compute $K_V=BHB^\top$ and the certified q values. If one pair has a certified q above threshold and a certified dominance gap, resolve that pair. If no pair exceeds the threshold, return no event. If the ordering cannot be certified or remains physically ambiguous, return unresolved or uncertified rather than using IDs.

The builder inserts one edge between the resolved vertices. It selects the distinct incident reference edges of those vertices, and assigns the new edge the CAN-REF-GM seed. That source set is nonempty because the q guard requires nonzero diagonal terms. Existing vertex positions are unchanged for A; the new edge's reference weight is added to its differential backend. For C, the complete target stable-edge reference map adds the new value. The structural base retains its old block and gives the new row and column zero. The target keeps the same candidate and temporal-realization family and numerical parameters, with graph-bound identities rederived. Its domain is not enlarged in response to admission failure.

Resource uses T=I and b=0 for current and reset. W and Z are handled by CAN-HRESET. The existing lifecycle constructs and readmits the target, including the accepted A initializer where applicable. No future ordinary trajectory is consulted to choose another pair.

This is **CL-29A — composed candidate completeness**: conditional on the declared present-read and reference constructors terminating, every semantic event input is determined. It is not yet proof that the event is a necessary expression of RC formation. That claim remains under **DB-27** and the causal-discrimination debt **DB-07**.

A useful bounded result follows from its graph grammar. With fixed n vertices and no other topology operations, each successful CAN-A event adds one previously absent unordered pair. Therefore the number of successful births is bounded by the number of initially absent pairs, at most $n(n-1)/2$. This is **DER-15**. It does not bound repeated failed attempts, computation per attempt, or graph growth when another family creates vertices.

CAN-A is a promising first *evaluation subject* because its new choices are sharply visible and it does not presume a classical RG2b derivative. That is not a recommendation to accept its physical interpretation before pressure.

## 12.3 CAN-B: structural-mode binary refinement

CAN-B binds CAN-STAGE-NOW with the conditional structural chart, CAN-S's simple separated mode and neighbor-mode partition, CAN-RES-U's unique locus rule, CAN-BIN's half-edge builder, CAN-TDY resource allocation from the present reconstructed current, CAN-REF-GM, CAN-KMASK, CAN-XDUP and CAN-HRESET.

The policy includes every threshold, reference scale, dyadic grid size and target-profile transformation rule. It reads a qualified structural chart rather than every arbitrary runtime state. At an active floor boundary, unresolved selector crossing, missing branch association, or unsupported derivative, it reports analysis unavailable; it does not pretend those conditions are topology pressure.

Once the mode and partition are admitted, the source determines both the graph split and the resource activity ratio. The same represented T is applied to current and reset. The complete target reference is constructed, the A initializer or C reconstruction is invoked, and the ordinary event lifecycle admits or rejects. No total-current singularity at an auxiliary A initializer state is inserted as an extra condition; no target failure alters the selected split.

**CL-29B** is a composition claim with more mathematical prerequisites than CAN-A. Its strongest unresolved link is the interpretation of the structural condition as a trigger for a *graph* refinement. The core says the mode alone does not determine the nonlinear outcome. CAN-B explicitly adds a new hybrid rule that does determine an event; the investigation must judge that new rule rather than misclassifying it as source inheritance.

Its negative controls should include a structural precursor that relaxes on the same graph, a true protected null, a source with no uniquely determined locus, a loop-bearing vertex outside CAN-S's lift domain, and a target whose fixed chart rejects after a valid graph build. Different failures belong to different claims.

## 12.4 CAN-C: state-conditioned coarsening, with an optional quotient certificate

CAN-C binds an adjacent-pair candidate set, CAN-Q's present resource and tendency residuals, a homogeneous score using declared scales, CAN-RES-U, CAN-MERGE-DROP with a fixed rule for all internal edges, unit-measure summation T, a midpoint A host-reference constructor, and CAN-HRESET.

A pair is eligible when its two residuals are below their bounds and its source graph/reference conditions hold. A unique eligible dominant pair is resolved; equal alternatives remain unresolved. Every external edge preserves its identity and outside endpoint, and parallel external edges remain distinct. The new target context must have an admitted lift, otherwise the event fails before publication.

The basic candidate is a fully specified *lossy state-conditioned merge law*. It is not an exact quotient because history reconstruction changes W/Z and because matching present resource tendencies need not persist. A stronger variant **CAN-CQ** activates the complete-state quotient or approximate intertwining certificate before admitting the same event. That is a different claimed law, not a post hoc label added to a successful CAN-C run.

**CL-29C** therefore branches. The weak composition can be evaluated while **DB-25** remains open. The exact quotient claim cannot. A viability-pruning variant changes the source guard to CAN-V and activates its own functional, threshold and core-correspondence debts. It should not be merged into CAN-C merely because both use the same graph quotient.

## 12.5 What would discriminate these proposals

The same graph can contain a source with nontrivial geometry-mediated nonedge coupling, a negative constrained mode, and two nearly redundant vertices. CAN-A, CAN-B and CAN-C may consequently predict different graph events or no event. That is not a defect in the investigation input. It is the question the input makes experimentally and mathematically addressable.

The first comparison should freeze the source family, context, causal-state construction, duration, history policy and numerical environment. It should compare the actual event preimages and complete poststates, not only vertex counts. A target-admission failure is recorded against that candidate's domain; it is not automatically evidence that another candidate is scientifically preferred.

Controls must also separate topology from history reconstruction. If every candidate resets all Z and reinitializes all W, a common effect may arise from the shared history treatment rather than the different graph laws. Identity-topology reconstruction and geometry-consumer-off controls can help identify that confound, but their exact implementation and source authority must remain declared.

The receiving machinery can then transform the claims independently: accept a numerical constructor, restrict a graph law's domain, reject an event guard, route a preserving history map, or retain an exact quotient as conditional. No aggregate “ATC works” verdict should obscure those outcomes.

---

# 13. The investigation should pressure the claims, not merely execute examples

## 13.1 Separate three kinds of evidence

The supplied derivations establish conditional mathematical consequences of their stated assumptions. The accompanying exact-arithmetic checks challenge selected finite constructions and counterexamples. Neither is a native GRCV4 event campaign.

A native campaign must name the complete profile, source code identity, source and reset state, reference/backend inputs, event policy and executed stage. It must distinguish a pre-existing accepted execution from a new test run. A current checkout may validate a new claim, but it cannot become the historical subject of an older receipt merely because its tests still pass.

The implementation baseline must be pinned before any new runtime attribution. This draft has inspected source documents and local attachments; it has not obtained and executed a dependency-complete checkout of the final two commits reported by the user. The source register and manifest say exactly which files were locally hashable and which were viewed through web retrieval. This limitation is **DB-01**, not evidence against the completed tranche.

## 13.2 Arithmetic discriminators

The first required arithmetic discriminator is the rounded-thirds case. It invalidates the old independently rounded coefficient recipe and supports the need for an explicit represented T. CAN-TDY must pass exact column sums, complement symmetry, midpoint ties and its error bound over varied activity ratios.

The second is the smallest-subnormal split. Even exact coefficients can lose stored mass on output. The test must inspect the actual rounded source/target charges and reset behavior. It must not silently call an exact real map an exact numerical conservation result.

The third is a round-once affine witness. With $\varepsilon=2^{-1074}$,

$$
 T=\begin{pmatrix}1/2&1/2\\1/2&1/2\end{pmatrix},
 \qquad C=(\varepsilon,\varepsilon),
$$

each exact component equals $\varepsilon$. Prematurely rounding the two products produces zero. This tests the event's declared arithmetic rather than approximate scalar agreement.

Reference-seed tests should include extreme positive finite weights, equal endpoints, permutation, exact representable roots, and intervals around rounding midpoints. A passing high-precision decimal comparison alone is not proof of the exact nth-root rounding recipe; exact midpoint comparisons provide the relevant discriminator for CAN-REF-GM.

## 13.3 Graph and representation pressure

The graph builder must be tested on loops with both ends assigned to one child and with ends separated across children. Parallel edges retain their identities. A merge must distinguish retained internal loops from explicitly dropped internal edges. Replacement must preserve its external boundary or explicitly declare a change.

Representation tests compare physical event classes under a supplied correspondence. They do not demand that coordinate-sensitive hashes remain unchanged. Inverse representation transport should recover scientific coordinates under the inverse map while retaining the two successful operations in lifecycle history.

Symmetry pressure must include an invariant source with two exchanged candidate loci. A unique-locus policy should not select one through IDs. A batch candidate should not be rejected merely because no single locus is distinguished; it should instead face its actual combined-map and admission obligations. Near-symmetry tests must separate physical state perturbations from storage-order changes.

## 13.4 Structural, temporal and interpretation controls

A protected null must not trigger CAN-S. An unavailable Hessian at an active kink must not be reported as $\alpha=0$. A positive structural form must not automatically establish temporal stability. A failed numerical certificate must not automatically become an instability witness.

Restoration tests must include a target in a known attraction basin that is not itself an equilibrium, and a structurally positive equilibrium under a temporally unstable discrete map. These are independent discriminators for the definition-level errors in the previous drafts.

Viability tests must vary only the additive normalization of the candidate functional. CAN-VABS should either bind the origin so the change is a different profile or report the changed threshold outcome honestly. CAN-VREL should preserve the stated invariance while retaining its anchor and scale as real new choices.

A graph event with unchanged derived basin organization must not receive a core topology attribution merely because an edge was added. A finite child-persistence witness must not receive a spark label solely because the horizon completed.

## 13.5 Causal and lifecycle pressure

Run the same scientific source with different telemetry, receipt grouping, zero-duration operations and serialization order. Under the initial causal projection, physical generator output must agree up to the declared representation. A retained-counter proposal is tested separately under its explicit memory law.

Late failures should be injected after the graph map, resource map, target reference, A initializer, current readmission, charge check, receipt construction and archive validation. Each failure preserves the correct transaction prestate. Under CAN-TIME-AFTER, that prestate is the already committed ordinary poststate. Under CAN-TIME-JOINT it is the macro-operation prestate; the two contracts must not be confused.

Native negatives must include a reset-only failure, an RG2b state-versus-next-step distinction, history-policy mismatch, missing target C reference edge, signed-zero contamination, nonfinite reference seed, and a programmer error inside an internal constructor. Return codes must preserve the originating stage rather than laundering every failure into a generic topology rejection.

Mixed-operation sequences are essential. A representative sequence is ordinary evolution, autonomous event, pure representation, migration, another ordinary step, explicit reconstruction, save/load, reset and reversion attempt. The exact chosen sequence should make some operations succeed and others fail for known reasons, with the persistent ledger prefix and known scientific-state commitments preserved.

## 13.6 False positives matter as much as successful events

A generator that can make one graph change is easy to produce. A generator that does not invent graph changes whenever a numerical margin narrows is harder.

The pressure campaign should therefore retain long or bounded-envelope no-event controls where the source remains in a known admissible restoring regime. The statement is not that every healthy organism must remain structurally immutable. The statement is that a claimed trigger should activate only according to its own physical law, not because of solver noise, stale state, an observation call, or an inappropriate use of a protected null.

For CAN-Q, equal current resource with different retained W/Z is a necessary control. For CAN-R−, zero current on an indispensable bridge is a necessary control. For CAN-R+, a nonedge geometric coupling that is already adequately consumed on the existing graph is a necessary challenge to the claim that edge birth is physically warranted.

## 13.7 What this draft's attached checks actually do

The attached `pressure_checks.py` executes only independent finite mathematical tests. It verifies the dyadic split's complement and error properties, the loop/parallel-edge combinatorial construction, covariance of the node-form relation witness, selected exact geometric-mean rounding cases, and several logical counterexamples used in the prose. It also checks that the local claim/debt index has reciprocal links and valid identifiers.

It does not import `pygrc`, run the accepted candidate solvers, instantiate an ATC profile, authenticate an event receipt, or prove native rollback. Its results are correctly labeled mathematical and editorial evidence. **CL-27** concerns the separation and retention of those evidence classes, with **DB-23** still required for runtime claims.

---

# 14. Claims, debts and the receiving investigation

## 14.1 The local records are proposals, not admitted side-tool nodes

The identifiers below make the draft addressable. They are deliberately prefixed `ATC7-` so they cannot be mistaken for accepted D10/D11 objects. Each claim has a precise statement in `proposal_index.json`, with assumptions, source references, debt edges and discriminating pressure. The compact tables here are navigation aids for the argument, not substitutes for it.

The claim kind matters. A conditional derivation can be checked from its stated premises without accepting the physical interpretation of the candidate that consumes it. A proposed integration contract needs native evidence. A source-interpretation claim needs the actual source and scope, not merely a similarly named historical identifier. No row in this draft has `accepted` status.

## 14.2 Claim index

All identifiers in this table expand to the `ATC7-` prefix. The debt numbers are navigation shorthand, not a statement that every debt universally blocks every version of the claim. The exact edge activation in the companion index controls: in particular, the behavioral quotient debt activates for CAN-CQ, not for the weak state-conditioned merge.

| Claim | Proposition / location | Bearing debt handles |
|---|---|---|
| `CL-01` | Scoped source inheritance — Chapter 1 | DB-01, DB-24 |
| `CL-02` | Physical generator and wire binding — Chapter 2;4 | DB-02, DB-03, DB-04, DB-21 |
| `CL-03` | Profile-correct analysis reuse — Chapter 2;3 | DB-03, DB-05, DB-06, DB-26 |
| `CL-04` | Conditional structural witness — Chapter 3;5.1 | DB-04, DB-05, DB-06, DB-07, DB-08 |
| `CL-05` | Geometry-conditioned relation witness — Chapter 5.4 | DB-03, DB-04, DB-07, DB-10, DB-27 |
| `CL-06` | Complete-state quotient coarsening — Chapter 5.3 | DB-06, DB-15, DB-25, DB-26 |
| `CL-07` | Functional-guarded pruning — Chapter 5.6;10.3 | DB-02, DB-03, DB-06, DB-17, DB-18 |
| `CL-08` | Equivariance constrains event classes — Chapter 4.4 | DB-10, DB-23 |
| `CL-09` | Certified unique resolution — Chapter 6.1 | DB-02, DB-09, DB-10 |
| `CL-10` | Invariant simultaneous event — Chapter 6.3 | DB-11, DB-14, DB-15, DB-21, DB-23 |
| `CL-11` | Half-edge binary refinement — Chapter 7.2 | DB-08, DB-10, DB-12, DB-23 |
| `CL-12` | Forward quotient graph construction — Chapter 7.3 | DB-12, DB-14, DB-15, DB-16, DB-26 |
| `CL-13` | Relation and replacement templates — Chapter 7.4;7.6 | DB-02, DB-11, DB-12, DB-14, DB-16, DB-27, DB-28 |
| `CL-14` | Vertex birth/death accounting — Chapter 7.5 | DB-12, DB-13, DB-14, DB-16, DB-17, DB-18 |
| `CL-15` | Exactly conservative dyadic split — Chapter 8.2 | DB-13, DB-10 |
| `CL-16` | Separate map and stored charge — Chapter 8.1;8.4;8.5 | DB-13, DB-16, DB-23 |
| `CL-17` | Target reference constructors — Chapter 8.6-8.9 | DB-12, DB-14, DB-16, DB-26, DB-28 |
| `CL-18` | Independent history policies — Chapter 9 | DB-15, DB-16, DB-21, DB-23 |
| `CL-19` | Reuse of accepted A initializer — Chapter 9.2 | DB-14, DB-16, DB-23 |
| `CL-20` | Specific R_coh correspondence — Chapter 10.1-10.2 | DB-13, DB-17, DB-18, DB-19, DB-20 |
| `CL-21` | Absolute/relative viability alternatives — Chapter 10.3-10.4 | DB-03, DB-06, DB-17, DB-18 |
| `CL-22` | Qualified restoration certificate — Chapter 10.5-10.7 | DB-05, DB-06, DB-19, DB-20, DB-23, DB-26 |
| `CL-23` | Finite persistence monitor — Chapter 10.8 | DB-20, DB-22, DB-23 |
| `CL-24` | Ordinary/event transaction composition — Chapter 11.1-11.5 | DB-21, DB-22, DB-23 |
| `CL-25` | Explicit causal history — Chapter 2.1;6.5;11.7 | DB-02, DB-03, DB-22, DB-24 |
| `CL-26` | Local work and event-rate bounds — Chapter 11.6;12.2 | DB-22, DB-28 |
| `CL-27` | Evidence class separation — Chapter 13 | DB-01, DB-23, DB-24 |
| `CL-28` | Mechanics, lineage and interpretation axes — Chapter 7.8;10.1 | DB-17, DB-20, DB-27 |
| `CL-29` | Assembled candidate completeness — Chapter 12 | DB-02, DB-14, DB-16, DB-21, DB-26 |
| `CL-29A` | CAN-A derivative-free relation birth — Chapter 12.2 | DB-02, DB-03, DB-04, DB-07, DB-09, DB-10, DB-14, DB-16, DB-21, DB-23, DB-26, DB-27 |
| `CL-29B` | CAN-B structural refinement — Chapter 12.3 | DB-02, DB-04, DB-05, DB-06, DB-07, DB-08, DB-09, DB-10, DB-12, DB-13, DB-14, DB-16, DB-23, DB-26 |
| `CL-29C` | CAN-C lossy coarsening and CQ strengthening — Chapter 12.4 | DB-02, DB-03, DB-07, DB-09, DB-12, DB-14, DB-15, DB-16, DB-23, DB-26, DB-25, DB-27 |
| `CL-30` | Complete event equivalence — Chapter 7.6;9.5 | DB-11, DB-13, DB-15, DB-21, DB-23 |
| `CL-31` | Preservation of lifecycle guarantees — Chapter 11.5 | DB-01, DB-16, DB-21, DB-23 |
| `CL-32` | Claim-local investigation admission — Chapter 14 | DB-01, DB-24 |

## 14.3 Debt index: activation is part of the debt

A debt exists because a particular claim tries to cross a particular boundary. The table records that activation and the corresponding closure requirement. Failure to close a strong basin or quotient claim must not erase a valid resource map. Conversely, a valid resource map cannot be used as evidence that the basin or quotient claim passed.

| Debt | Activated question | Required closure |
|---|---|---|
| `DB-01` — Source and execution-subject admission | Any assertion about current source authority or native Tranche-7/ATC execution. | Pin repository commits, source bytes, release, dependencies and exact results. Retrieved main pages and older local attachments cannot stand in for the final execution subject. |
| `DB-02` — Endogenous constitutive closure | A proposal claims that the event is generated by the permitted scientific state. | Name every causal input and choice; close guard, resolution, construction, identity and outcome rules; challenge administrative and hidden-state dependence. |
| `DB-03` — Temporal stage and historical operand | A witness uses consumed current, threshold crossing, or a previous state rather than the declared present reconstruction. | Bind the exact stage and all required past preimages; show replay and reset semantics. |
| `DB-04` — Analysis-to-constitutive consumption | A source analysis object becomes a physical event guard. | Admit the successor consumer, stage and complete-profile identity without relabeling a diagnostic as an existing actuator. |
| `DB-05` — Branch and regularity applicability | A claim uses a structural chart, current slaving derivative, or classical section derivative. | Supply the exact branch, association, domain and derivatives; retain RG2b Lipschitz alternatives and kink/rank boundaries. |
| `DB-06` — Functional, tangent, metric and normalization | A claim invokes structural alpha, joint-state energy or magnitude comparisons. | Instantiate the complete functional and constrained domain; distinguish fixed W from temporal W/Z variation; remove/classify nulls. |
| `DB-07` — Physical discrimination of a trigger | A numerical or structural witness is claimed to warrant an RC topology response. | Retain no-event and consumer-off controls; distinguish softening, numerical certification, history loss and actual graph-response effects. |
| `DB-08` — Mode-to-locus and half-edge lift | A mode or response is claimed to determine graph surgery. | Specify coordinate meaning, sign/degeneracy handling, loops, partition and covariance; compare competing lifts. |
| `DB-09` — Within/across-family resolution order | A law compares candidates or operation families. | State units, score/order/exclusivity, margins and unresolved outcomes; do not infer cross-family comparability. |
| `DB-10` — Finite-precision equivariance and threshold certainty | Exact covariance or stable physical decisions are claimed in a numerical implementation. | Use exact comparisons/enclosures or declared robust domains; challenge relabelings, orientations and threshold ties. |
| `DB-11` — Batch and sequential critical pairs | Disjoint events or an atomic rewrite are claimed equivalent to sequential edits. | Prove combined reference/history/resource maps, intermediate admission, and required equality notions; account for global reset effects. |
| `DB-12` — Complete finite graph/template mechanics | A template is claimed graph-generic or collision-free. | Close endpoint roles, loops, parallel edges, fresh IDs, boundary mappings and any finite template grammar. |
| `DB-13` — Represented resource law and actual charge | Real coefficient conservation is promoted to an executable or exactly closed event. | Bind representable coefficients and rounding, validate both roles and actual charge; no silent residual correction. |
| `DB-14` — Target reference, backend and context | A new graph is claimed to have a complete target package. | Construct every target coordinate, reference seed, structural base, backend, context and complete-profile identity under fixed domains. |
| `DB-15` — History transport or explicitly declared loss | A topology map is claimed to preserve or transform W/Z history. | Supply separately typed channel maps and source/target lineage, or retain honest reconstruction/loss; never infer from shape or resource T. |
| `DB-16` — Initializer and whole-role target integration | A constructed target is claimed fully admitted. | Use the accepted initializer order and independently reconstruct current/reset; preserve target numerical and atomic failures. |
| `DB-17` — Core object and topology correspondence | An event is called an R_coh, basin, spark, or identity-topology event. | Map substrate state to the exact spatial/support/finite-continuation objects and demonstrate the requested change. |
| `DB-18` — Viability functional and threshold | A guard is identified with core viability or compared across graphs. | Bind functional/sign/normalization/anchor/units/locus and threshold or crossing; distinguish relative proposals from V=-P. |
| `DB-19` — Restoration and actual dynamics | A target is claimed inside a stable basin or an attracting set. | Prove the specified basin/equilibrium/Lyapunov certificate for the actual relevant state and dynamics, with numerical-error and hybrid-loop scope. |
| `DB-20` — Finite persistence to identity/formation | Finite observation or graph structure is promoted to spark, identity, reflexive closure, or native formation. | Supply the additional core-specific basin, attraction, invariance, closure and provenance evidence. |
| `DB-21` — Atomic composition and publication closure | An ATC wrapper is claimed to preserve lifecycle guarantees. | Define transaction boundaries and report composition; verify target and prospective archive before publication; preserve programmer-error semantics. |
| `DB-22` — Causal memory, timing and event rate | Refractory counters, probes, crossings, repeated attempts, or non-Zeno claims are activated. | Declare causal history and lifecycle maps, eligible boundaries, work bounds and clock assumptions; distinguish finite beats from physical time. |
| `DB-23` — Native execution and reproducible evidence | The proposal claims actual GRCV4 execution, covariance, replay or rollback. | Run the admitted exact subject with independent expectations, retained failures and source-bound captures. |
| `DB-24` — Investigation and side-tool source admission | Local ATC records are to become queryable scientific authority. | Use the actual source-observation/classification/adapter/readmission/rebuild/audit/acceptance route; preserve reciprocal claim/debt lineage. |
| `DB-25` — Complete quotient or behavioral approximation | A merge is claimed to preserve or approximate complete behavior. | Supply H on every causal coordinate, domain invariance, exact or bounded intertwining, and target Lipschitz constants. |
| `DB-26` — Complete-profile target applicability | A family-level formula is promoted to multi-profile support. | Record exact domains and targets for all ten products; preserve unsupported cells without weakening the realization. |
| `DB-27` — Relation/coarsening semantic driver | Present coupling or inactivity is called missing relation, redundancy, death or extinction. | Demonstrate the operation-specific causal meaning; test zero-current bridges, hidden W/Z, existing nonedge mediation and delayed effects. |
| `DB-28` — Finite search/work and objective interpretation | A finite partition optimizer or template grammar is treated as scalable or core-derived. | Bind objective and search semantics, complexity/work budgets and exact outcome independence; distinguish computational failure from physical absence. |

## 14.4 Existing lineage to consume without rewriting it

The source-based structural candidates should begin from the existing D8/D10 formula and domain lineage, including `D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL` and, where a mixed A metric is claimed, `D10-VERIFY-A-ANALYSIS-METRIC`. These are not newly discovered universal blockers. They are existing stronger-claim obligations whose exact current dispositions must be retrieved from the admitted source bundle.

The RG2b differentiability boundary is especially useful precedent. `GTRS-RG-DEBT-C1-SECTION-REGULARITY` was narrowed so a bounded result could survive while a stronger derivative claim remained conditional. Draft 7 uses that pattern, not a claim that RG2b is scientifically incomplete until every derivative exists. The relation to `D10-CL-O-005` and `D10-CL-C-009` should be preserved exactly when the current accepted bundle is queried. [S08, S09]

For Candidate C differentiation, `D11-C-EC-C-J0-DERIVATIVE` identifies the baseline derivative obligation. For initializer lineage, `D10.2-EC-PARENT-L-A-INITIALIZER-GRC` supplies historical contract provenance, while the later reference-pass successor supplies the actual producer choice. A query of the older node alone cannot prove that the newer initializer was already selected there. [S05, S12]

The `L-TOPOLOGY-EVENT`, `CORE-C-AUTHORITY` and profile-governance objects identify the downstream contract that ATC consumes. General history transport, new causal ATC memory, and analysis-driven event consumption must enter as explicit successors of their earliest affected contracts. They do not retroactively alter the existing source population.

## 14.5 A worked claim transformation

Suppose the investigation accepts CAN-BIN's multigraph construction and CAN-TDY's exact coefficient rule, but finds that the CAN-S mode lift fires on states that restore entirely within the existing graph and has no defensible constitutive interpretation. The correct outcome is not simply “binary refinement rejected.”

CL-11 can remain a bounded graph-construction result. CL-15 can remain a bounded arithmetic result. CL-29B is restricted, replaced, or rejected as an assembled autonomous law, with DB-07 transformed and the negative controls retained. Another generator could later reuse the accepted builder and arithmetic without inheriting the failed trigger. The reciprocal claim/debt edges record that change.

Conversely, if a quotient certificate closes for a restricted C regime, CL-06 can gain bounded support and CAN-CQ can gain that scope. It does not follow that A with independently retained W or a persistent profile has the same quotient. Their unsatisfied full-state map debts remain local.

This is the intended use of the machinery: scientific progress changes claims and their relations, rather than merely turning an “open” flag into a “resolved” flag. [S08]

## 14.6 Admission into the existing side tool

The published guide describes a source-observation and readmission boundary. New file discovery does not make a record accepted authority. The documented path includes classification, adapter/readmission work, successor bundle construction, graph/reference conformance, rebuilding derived material, audit and acceptance. [S09]

Accordingly, `proposal_index.json` is not a ready-made side-tool import. It has an intentionally local schema. Its purpose is to prevent an adapter author from guessing the intended claim/debt edges. The receiving process should first reconcile these local fields with the actual admitted source schema and authority model.

Once admitted records exist, the current guide's `contract_provenance`, `reconstruction_path`, `debt_lifecycle`, `candidate_career`, and source-observation workflows can trace them. Draft 7 does not call those tools on invented IDs, claim a returned classification, or mutate the accepted graph. Counts, visual position and dependency reach must not become ranking evidence.

## 14.7 Investigation order follows dependencies rather than a mandatory catalogue

A sensible first act is source and contract admission: pin the relevant core, GRCV4, event supplement, release, implementation and prior-debt subjects. Then select a concrete claim to pursue, such as the derivative-free CAN-A assembly, the CAN-B structural lift, or the strong CAN-CQ quotient. The choice activates different debts. It need not wait for every other operation family to be solved.

Within a selected lane, derive the witness and causal consumer, close the exact graph/resource/reference/history construction, and execute the full target lifecycle. Only then promote the particular native claim its evidence supports. Stronger Appendix-D, identity or spark claims activate their own correspondence and restoration obligations when attempted.

This is not an instruction to abandon broad scope. All families remain explicitly dispositioned. It avoids making eleven operation names into eleven compulsory investigations regardless of which mathematical dependencies actually arise. A rejected candidate and a restricted support cell are useful results when their claims and debts remain visible.

---

# 15. Proposed records and preservation of the earlier work

## 15.1 A record should identify a claim-bearing construction, not create another physics layer

The previous drafts developed useful record ideas, but several record names assumed that a selector, episode or spark-completion stage already had authority. Draft 7 keeps the information while removing that assumption.

A proposed ATC profile record binds the base complete profile and the new theta: causal projection, eligible evolution boundary, witness family, exact guard and resolution rule, graph template, resource recipe, reference/context constructors, history policies, required target claims, and numerical work limits. Its identity must exist before a particular event output is computed. An output-bearing event witness must not be used to compute a static profile identity that the same witness already references.

A witness record binds the source physical input, reconstruction stage, relevant operator or present surface, normalization, numerical enclosure, physical locus, and any derived partition. Its values are evidence of recomputation, not a substitute for source inputs during import. A result record distinguishes no event, unresolved, uncertified, resolved-but-rejected, and committed outcomes without appending failed evidence to the successful scientific ledger.

An event record then reuses the existing request, initializer-pair, receipt, and transition archive contracts as far as they apply. If the new wrapper needs to retain the generator witness or a causal memory coordinate, that is an explicit successor-schema question. It is not resolved by adding arbitrary keys to an old closed payload.

The proposed shapes are summarized below because an implementer needs to see which information goes where. They are not admitted schemas.

| Proposed record | Claim-bearing content | What must not be smuggled into it |
|---|---|---|
| Static ATC policy | base profile, theta, source lineage, algorithms and domains | a chosen future result or mutable caller callback |
| Present witness | exact source projection, stage, derived evidence and certainty | cached authority replacing a fresh reconstruction |
| Physical prescription | resolved graph/locus action and fixed construction policies | unchosen target references or caller-supplied split weights |
| Bound event request | actual source identities, role mappings and existing event fields | a second physical chooser at serialization time |
| Attempt result | resolved/unresolved/uncertified/rejected/committed and stage | a scientific failure code for an internal programmer exception |
| Optional causal memory | explicit update/reset/migration/transport contract | orchestration-only timers that alter dynamics |
| Core-attribution evidence | exact additional assertion, source mapping and certificate | an automatic spark or identity label inferred from graph shape |

The metadata should allow the receiving machinery to reconstruct why a proposal made its event, not merely reproduce a hash of the answer. At the same time, no finite metadata trail can establish that an externally supplied historical execution actually occurred. It can establish internal consistency and correspondence with the declared inputs and laws.

## 15.2 Support should be an exact surface, not an inflated label

A future release can advertise a generator only through its exact complete profile, theta, operation template, numerical domain and required assertion set. A derivative-free relation-birth profile and a structurally qualified refinement profile are different support entries even if both call the same event executor.

The proposed conformance progression is consequently claim-based. First establish the derived witness and its null/covariance behavior. Then establish resolution and complete construction. Then execute the native lifecycle with failure preservation. Separately establish any quotient, viability, basin, identity or spark interpretation being claimed.

This replaces the earlier AT0–AT4 ladder without losing its useful evidence obligations. A passing refinement case no longer advertises autonomous coarsening. A finite persistence monitor no longer implies spark. An unsupported classical RG2b derivative no longer blocks a derivative-free geometry witness. All ten family/realization products still receive explicit dispositions for any claimed support surface.

## 15.3 The preservation ledger records a transformation, not just a word count

Earlier revisions attempted preservation by appending whole older drafts. That made the document longer without making its precedence rules coherent. Draft 7 instead assigns each major idea a current location and disposition. Live alternatives remain in the body where they compete. Superseded interpretations are recorded below rather than repeated as instructions.

The original files remain source history; their local hashes are recorded in the companion manifest. This ledger does not delete them or rewrite their text. It tells the investigation how Draft 7 changes their claims.

| Earlier material / location | Draft-7 disposition and location | Reason for transformation |
|---|---|---|
| Draft 1 opening: missing front half of topology | Retained — Chapters 1–2 | The missing generator remains the central question, grounded in existing maps |
| Drafts 1–6.1 three maps | Retained as possible factorization — Chapters 2, 4 | Three helpers are not three agents or a derived law by themselves |
| Draft 2 ten-profile correction | Retained and qualified — §2.4, Chapter 3 | Exact applicability replaces ten presumed copies of one analyzer |
| Draft 3 investigation-first boundary | Retained — opening and Chapter 14 | A proposal is input to claim transformation, not accepted authority |
| Drafts 3–6.1 generic chronology of core terms | Replaced — Chapter 1 | Clause-specific lineage avoids silent replacement of older meanings |
| Draft 6.1 restoration as formed-branch membership | Withdrawn — §10.5 | Basin membership, equilibrium and a branch are different predicates |
| Draft 6.1 global viability/sign blockade | Restricted — §§10.3–10.4 | Specific functional/normalization debts replace a universal stop condition |
| Drafts 1–6.1 no chooser/observer | Retained causally — Chapter 4 | Deterministic evaluation is not automatically extrinsic choice |
| Drafts 4–6.1 no numerical search or future-computation rule | Restricted — §§4.2, 5.2, 10.6 | Evaluating a fixed relation/certificate differs from an undeclared future tournament |
| Drafts 1–6.1 unique maximum selector | Retained as CAN-RES-U — §6.1 | It is a candidate constitutive rule, not inherited core law |
| Exact symmetry implies no event | Replaced by DER-03 — §§4.4, 6.3 | An invariant batch or unordered event can also be equivariant |
| Unordered mode sign handling | Retained — §§5.1–5.2, 7.2 | Sign exchange must not select a physical child |
| Universal local tuple Sigma/g/H/M/chi/L | Retained as a restricted candidate — Chapter 3 and CAN-S0 | Existing constrained structural mathematics comes first |
| Pressure P=ID chi | Retained explicitly as CAN-S0 — §5.1 | Susceptibility is not a proved topology trigger |
| Capacity/saturation factor | Retained optional — §5.1 | No generic degree cap; GRC9 remains specialization |
| Refractory period and episode age | Retained as CAN-MEM — §§6.5, 11.7 | Reconstructibility alone does not justify causal history |
| One event per boundary | Retained initial scheduling candidate — §11.1 | Not a universal symmetry or core constraint |
| Simultaneous disjoint events | Expanded as CAN-RES-B — §6.3 | Complete history/reference critical pairs matter |
| Binary refinement | Retained and completed for multigraphs — §7.2 | Half-edge roles remove loop ambiguity |
| Deterministic child and edge IDs | Retained — §6.4 | Naming follows physical resolution and collision admission |
| Current-weighted resource split | Retained as CAN-TDY and alternatives — §§8.2–8.3 | Exact represented coefficients close the old rounding gap |
| Equal zero-activity split | Retained — §8.2 | Explicit zero-denominator convention; not a missing-current default |
| Same map for current and reset | Retained — §§8.1, 8.4 | The event is one declared map, evaluated on two states |
| Geometric-mean edge reference | Retained with exact rounding candidate — §8.6 | Positive real formula and finite recipe are distinct |
| Structural-base surviving-star restriction | Restored in full as CAN-KMASK — §8.7 | It had been reduced to a policy name in later drafts |
| Duplicated A child positions | Restored as CAN-XDUP — §8.8 | No arbitrary host direction; WLS/domain claims remain bounded |
| C reference-map lift | Retained — §8.9 | Exact target live-edge coverage precedes rederivation |
| Context lift | Retained — §8.9 | Graph-dependent context cannot be silently copied |
| History reconstruction/loss baseline | Retained as CAN-HRESET — Chapter 9 | Honest first policy, with explicit topology/history confound |
| History-preserving improvement | Retained as CAN-HINJ and stronger pushforwards — §9.3 | Smaller preserving candidates need separate authority |
| OS/CI/RG2b/PC/CI+PC target endings | Corrected — §2.4 and §11.3 | State readmission is not necessarily another ordinary beat |
| Broad directionality H9 | Retained — Chapters 5, 7, 12 | Refinement is not privileged as the only endogenous direction |
| Forward coarsening | Expanded as CAN-Q/CAN-C/CAN-CQ — §§5.3, 7.3, 12.4 | Weak merge, approximate quotient and exact quotient are separate claims |
| Pruning and extinction | Retained as interpretations with distinct guards — §§5.6, 7.5, 10 | They are not primitive graph shapes or synonyms for every merge |
| Edge birth/death | Expanded with explicit witnesses — §§5.4–5.5, 7.4 | Existing mediated coupling and zero-current bridges are discriminators |
| Rewiring | Retained — §7.4, §9.5 | Relation lineage distinguishes it from death plus birth |
| Pure node birth/death | Retained with conservation boundary — §7.5 | Resource origin/destination and reference domain are explicit |
| Atomic module replacement | Retained with two concrete templates — §7.6 | A target synthesis rule replaces “build a better module” |
| Inverse sibling reversion | Retained — §7.7, §11.7 | Inverse topology does not resurrect old dynamics or erase receipts |
| Multi-beat child stabilization | Retained as finite evidence — §10.8 | Finite persistence alone does not establish a spark or attractor |
| P/G/R/I tier ladder | Replaced by independent assertions — §10.1 | No universal graph-event-to-identity hierarchy is inherited |
| Tier-P universal prohibition | Withdrawn as a core conclusion — §10.9 | Compatibility remains claim-local; lack of proof is not a theorem of impossibility |
| Resource conservation bridge | Retained precisely — Chapter 8 | Current fixed pairing and actual rounded charge remain separate |
| Candidate and selection record ideas | Integrated — §15.1 | Static policy, witness, binding and attempt evidence have distinct roles |
| AT0–AT4 and twenty-vector programme | Integrated and broadened — Chapters 13, 15 | Claim-specific native evidence replaces refinement-only labels |
| GRC9 crosswalk | Retained — §15.4 | No generic claim is backfilled from nine-port mechanics |
| Investigation plan | Replaced by claim-activated dependency flow — §14.7 | The machinery should adjudicate concrete claims, not a compulsory catalogue |
| Prior audits and purification findings | Retained as evidence/proposal history — S15, S16 | A review recommendation is not automatic scientific acceptance |

## 15.4 GRC9 remains a source of bounded comparisons, not a generic shortcut

The GRC9 specialization gives source conditions, mechanical construction, chirality/growth choices and post-event notions that can be compared with this architecture. The comparison should identify which parts are already state-determined, which are externally declared event inputs, and which are specialization-specific constraints.

It must not infer that a generic degree threshold replaces nine-port saturation, that binary refinement is equivalent to the same-port expansion, or that a finite child-stabilization test is a universal spark theorem. A future autonomous GRC9 policy can be another complete candidate under the same claim/debt discipline, but the crosswalk itself does not supply generic authority. [S05 Appendix A]

## 15.5 The eventual paper can be smaller because the investigation record is richer

Draft 7 is deliberately proposal-rich. The eventual accepted paper need not contain every candidate. If CAN-R+ fails as a physical edge-birth law, its covariance lemma may still be useful while the trigger is rejected. If an exact quotient closes only for a restricted C domain, the paper should state that scope rather than enlarge it for symmetry. If a full viability bridge is not needed by a surviving operational graph law, it should not be forced into that law's proof.

The important preservation object is the claim transformation and its evidence. That is what allows the final paper to become elegant without erasing the investigation that earned it.

---

# 16. Source register and evidence boundary

## 16.1 How to use the sources

The source labels below identify what was actually used. The primary core, paper, specification and machinery documents were consulted through web text retrieval during preparation. Those retrieved `main` pages are not a commit-pinned source bundle. Local uploaded files can be hashed, and their hashes are retained in `source_manifest.json`; a web page is not falsely assigned a byte hash that was never computed.

The user's reported Tranche-7 completion is the intended runtime frontier. This preparation did not obtain the final two commits as a dependency-complete executable checkout, did not run the side tool, and did not rerun Tranche-7 conformance. Some local artifacts are explicitly earlier drafts or execution records. Their content supports the stated contracts or lineage only within the scope recorded here. They do not establish that a later implementation still has an old defect, or that every later correction has independently been reproduced.

### S01 — Reflexive Coherence, November 2025

The exact uploaded `2025-11-ReflexiveCoherence.md` is the primary source for the coherence-only formulation, Appendix-Zero derived graph, Appendix-D topology-changing operator, and Appendix-J viability statement. Appendix C and the potential discussions contain the sign and basin-language issues explicitly discussed in Chapter 1. The uploaded bytes are hashed in the manifest.

Repository reference: `urosj/geometric-reflexive-coherence/core/2025-11-ReflexiveCoherence.md`.

### S02 — Identity, Choice, and Abundance, November 2025

`2025-11-RC-IdentityChoiceAbundance.md` supplies the identity, choice/collapse, spark and abundance lineage. Draft 7 follows the distinction between a choice situation and its collapse event without turning that terminology into an automatic description of `Resolve_topo`. Its stronger general abundance narrative is read with S03's later qualifications.

Primary text: [2025-11-RC-IdentityChoiceAbundance.md](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2025-11-RC-IdentityChoiceAbundance.md).

### S03 — The Continuation Spectrum, August 2026

`2026-08-TheContinuationSpectrum.md`, especially Formal Status, constrained variation, the separation of spectra, the functional-sign convention, the full geometry chain, temporal closure, accommodation and the discussion of structural marginality. Draft 7 uses its conditional mathematical structure and its limits; it does not import a local continuum mobility closure into every GRCV4 profile.

Primary text: [2026-08-TheContinuationSpectrum.md](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-TheContinuationSpectrum.md).

### S04 — Read-Back, August 2026

`2026-08-ReadBack.md`, especially Formal Status, the retained/current response, write-back, the distinction between kinetic and structural effects, and the threshold/choice discussion. The no-additional-chooser statement constrains causal interpretation. It is not used as a blanket ban on deterministic evaluation of an admitted relation.

Primary text: [2026-08-ReadBack.md](https://github.com/urosj/geometric-reflexive-coherence/blob/main/core/2026-08-ReadBack.md).

### S05 — GRCV4 mathematical paper

`implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md`. The retrieved text carries date 2026-09-11 and describes itself as a design paper with initializer integration awaiting paper review. Relevant sections are §§1–3 on architecture and authority, §§5–10 on causal roles and realizations, §12 on lifecycle/events/initialization, §13 on structural and temporal analysis, and Appendix A on GRC9 specialization.

This status is the paper's own evidence boundary. It is not evidence that the user-reported later implementation completion did not occur.

Primary text: [2026-09-GRC-V4.md](https://github.com/urosj/graph-reflexive-coherence/blob/main/implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md).

### S06 — GRCV4 extraction/provenance proposal

`drafts/GRCV4-proposal.md` is used for provenance and correspondence with investigation objects. It is not treated as an independent scientific derivation merely because it repeats an equation from the accepted investigation.

Primary text: [GRCV4-proposal.md](https://github.com/urosj/graph-reflexive-coherence/blob/main/implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md).

### S07 — GRCV4 normative specification

`specs/grc-v4-spec.md`, especially state authority, charge, analysis interfaces, complete-profile identity, lifecycle/events and receipt-parent admission. Its current analysis interface explicitly separates analysis objects from writers and retains the RG2b Lipschitz boundary. Its fixed charge covector is not replaced by the core moving-measure expression in this draft.

Primary text: [grc-v4-spec.md](https://github.com/urosj/graph-reflexive-coherence/blob/main/specs/grc-v4-spec.md).

### S08 — D10 synthesis and debt/claim transformation

`decisions/D10DesignSynthesisAndSpecWritingDecision.md`. The retrieved decision identifies itself as `accepted_bounded`, record `GRC9V4-CD-D10-v1`, with decision digest `3e673b335ad428d01006f231765d060a9bdd5f134332b143048f774de94bad00`. The specific relevant content is the governing claim/debt rule, reciprocal relations, claim classes and transformed-debt examples.

Draft 7 does not overwrite that topology, its population, or its historical dispositions.

Primary text: [D10DesignSynthesisAndSpecWritingDecision.md](https://github.com/urosj/graph-reflexive-coherence/blob/main/implementation/investigations/grc9v4-constitutive-design/decisions/D10DesignSynthesisAndSpecWritingDecision.md).

### S09 — Investigation plan and side-tool guide

`GRC9V4ConstitutiveDesignPlan.md` supplies the authority and claim-local activation discipline. `tools/exploratory-side-tool/docs/AgenticQueryGuide.md` supplies the inspected forensic-query and source-readmission workflow. The latter is a guide to an admitted tool, not evidence that this preparation executed it.

Primary texts: [investigation plan](https://github.com/urosj/graph-reflexive-coherence/blob/main/implementation/investigations/grc9v4-constitutive-design/GRC9V4ConstitutiveDesignPlan.md) and [AgenticQueryGuide.md](https://github.com/urosj/graph-reflexive-coherence/blob/main/implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/AgenticQueryGuide.md).

### S10 — Topology-event reconstruction and representation boundary

The local `grc-v4-topology-event-spec(1).md` supplies the checked event-resource arithmetic and separate history/representation policies. Its hash is compared against the available P9-7.3 record in the manifest. Its own earlier status heading is preserved; the source is not relabeled as a fresh runtime execution.

Repository target path: `specs/grc-v4-topology-event-spec.md`.

### S11 — Representation and lifecycle evidence contracts

The local representation-transport supplement and available event/lifecycle sources are used for signed coordinate action, distinct receipt groups, exact-action versus numerical charge evidence, source/target binding, and the distinction between state and step admission. Not all local code versions match the later P9-7.3 source bindings. The manifest records the exact available versions instead of implying a complete final checkout.

Repository paths include `specs/grc-v4-representation-transport-spec.md`, `src/pygrc/models/grc_v4_events.py`, and `src/pygrc/models/grc_v4_lifecycle.py`.

### S12 — Candidate A target-reference-pass lineage

The local `P9CandidateAInitializerReferencePassProposal.md` is an earlier proposal in the producer's lineage, not by itself the later acceptance. S05 §12.6 and the event supplement are used for the subsequently selected construction and its role. The distinction between auxiliary conductance, reference baseline, full final conductance and final target readmission is preserved.

The exact successor static policy and runtime/release source must be rebound before a new native ATC initializer claim. Older D10.2 provenance alone is not a substitute.

### S13 — Tranche-7 supplied records

The local P9-7.3 history-policy record and review, earlier migration/event/lifecycle records, and supplied audit artifacts identify particular tested claims and source hashes. They are used as evidence and lineage, not as a substitute for unavailable final source bytes. The manifest reports exact local hashes and any matches against the available P9-7.3 source inventory.

### S14 — Numerical implementation attachments

The available candidate, CI, PC, RG2b, graph-RG2b, geometry and resource-step sources illuminate the actual state and numerical owners. Their roles are cross-checked against S05/S07. Historical attachment versions are not silently treated as the latest implementation. No production module is executed by this draft's independent mathematical checks.

### S15 — Draft-6.1 purification review

`ATC-Draft6.1-PurificationReview.md` and its exact countermodels are review evidence. Their recommendations were assessed and integrated into Draft 7; they are not accepted ATC authority. In particular, the subsequent user correction that proposals should remain substantive and claim/debt-accountable governs how the review is used.

### S16 — Drafts 1–6.1 and their reconciliations

These are the local proposal history. Chapter 15 records the disposition of their important mechanisms. The manifest hashes the files so that future transformations can identify the actual predecessor bytes, rather than a remembered summary or a misleading size comparison.

## 16.2 What has been checked while preparing Draft 7

The companion files retain the independent mathematical checks and local index integrity results. They demonstrate only their stated arithmetic, matrix, finite-graph and record-consistency properties. They do not establish that a proposed generator satisfies the core, that a GRCV4 target admits, or that an ATC source bundle has been accepted.

The receiving investigation can now pin the actual repository subjects, admit this proposal as an input source, choose a claim to pursue, and retain the resulting transformations. That is the next scientific step—not declaring the whole draft true and not deleting its alternatives for the sake of a shorter final paper.

---

# 17. Closing proposition

The strongest question in this draft is deliberately small enough to be exact:

> Can one explicitly declared constitutive extension of GRCV4 generate a complete graph event from its legitimate causal state, while preserving the existing ordinary dynamics and lifecycle meanings, and can the resulting event earn precisely the additional claims made for it?

The answer is not supplied merely by a clean architecture. It requires a law. Draft 7 supplies several such proposed laws and decomposes their burdens instead of hiding them behind “topology pressure.” It also supplies common constructors and conditional derivations that can survive even if a particular law fails.

The receiving machinery should therefore be able to do more than accept or reject ATC as a whole. It should be able to say: this source interpretation holds; this numerical split is sound; this half-edge construction is complete; this trigger overclaims; this quotient is valid only on a restricted domain; this history map remains unearned; this target certificate proves basin membership but not spark; and this assembled candidate now has the evidence needed for a bounded successor.

That is the intended result of the revision. The draft is complete enough to investigate, but not presented as the investigation's conclusion.
