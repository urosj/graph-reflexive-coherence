> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

**Yes. These should be treated as outstanding requirements for the intended GRCV4 extension—not as permanent omissions that become acceptable merely because the report labels them accurately.**

My previous verdict needs a sharper distinction:

$$
\boxed{
\text{ATC-2’s bounded results are sound}
\;\neq\;
\text{ATC has completed the functionality we set out to build}.
}
$$

The submission is careful about its limitations. But **correctly documenting a missing capability does not satisfy the requirement to provide it**. My recommendation to proceed to ATC-3 was appropriate for adjudicating individual results; it should not be read as recommending final scientific synthesis around the current incomplete capability set.

Your concern is therefore justified. Without an explicit completeness requirement, the investigation could gradually redefine “generic autonomous topology” as whatever happened to work in the first few fixtures.

## 1. We need common capabilities, not identical dynamics

There is an important distinction between two kinds of difference.

It is legitimate for A_OS and C_PC to produce different currents, develop different structures, or resolve a topology event at different states. Their constitutive and temporal equations differ.

It is a different matter if choosing OS means that edge birth is structurally unavailable, choosing RG2b means that refinement has no defined generator, and choosing another realization means that both operations exist.

That would make the realization choice determine not only **how the organism evolves**, but **which structural operations the organism can ever perform**.

Such a difference could eventually be justified by the mathematics. But it must not arise accidentally from our first choice of witness or from incomplete implementation.

The target I would recommend is:

> **Every required topology capability must have a justified, non-vacuous realization across the ten candidate–realization families, within explicitly admitted domains. Their event conditions and trajectories need not be identical.**

“Non-vacuous” matters here. A function that always returns `no_event` may be a correctly implemented predicate, but it does not establish an operational edge-birth capability.

This does **not** mean every initial condition must eventually split, or every parameter choice must admit every target. Stable states, unresolved symmetry, numerical limits and genuine target rejection remain legitimate. It means that, for each required capability and family, there must be a scientifically justified domain in which the capability actually works—not only a method name or a successful read.

ATC-2 explicitly distinguishes its ten read probes from ten enabled ATC products. Its one-edge fixtures have no candidate nonedge, and their only merge would produce an edgeless target outside the constructor’s claimed domain. Those tests are useful, but they do not establish the functional coverage you are asking for. 

## 2. Splitting is not a peripheral omission

The missing split law is especially significant because the two concrete ATC-2 laws do not provide autonomous vertex growth at all.

Under the stated constructors,

$$
\Delta |V|=
\begin{cases}
0,&\text{edge birth},\\
-1,&\text{pair merge}.
\end{cases}
$$

The supplied-partition split constructor increases vertex count, but its partition is not generated endogenously. ATC-2 expressly holds that trigger. 

Consequently, **any sequence made only from the two currently concrete endogenous proposals has nonincreasing vertex count**:

$$
|V_{k+1}|\le |V_k|.
$$

This is a direct consequence of their graph maps, not an additional experimental finding.

So “we tested an increasing and a simplifying operation” needs qualification. Edge birth increases the number of relations; it does not provide the refinement capability that creates additional resource coordinates.

For the intended extension, I would now make **endogenous refinement a required scientific closure**, not an optional enhancement after the paper.

### The constructor is progress; the generator remains the main task

For the present structural proposal, the missing work is identified clearly: the qualified complete reduced functional, its chart and regularity, admissible tangent and metric, critical branch, selected mode, and equivariant mode-to-half-edge lift. The proposal correctly refuses to substitute a convenient matrix for that construction. 

Those are precisely the objects the investigation should now try to derive and validate.

There are two legitimate routes.

One is to close the structural-mode proposal on its proper domains and establish how its capability extends across the ten products.

The other is to derive a different, source-grounded refinement law where the structural-mode construction is inappropriate. That alternative must have its own claim and semantics. It cannot be called the same structural-instability law merely because it eventually invokes the same split constructor.

For RG2b in particular, a classical spectral route would activate its unresolved regularity obligations. A derivative-free route might avoid that specific dependency, but it would need its own derivation. The existing Lipschitz limitation is a constraint on the route—not permission to stop investigating refinement for that realization. 

**A held trigger should therefore remain a blocker for the required splitting capability.** The passing builder should be retained, but it cannot discharge that blocker.

## 3. The OS result should trigger a design investigation—not become the final OS feature set

The known OS limitation is stronger than “we have not found a positive example.”

Under K0, OS uses a candidate-current read at the reference Hodge, without an OS pass. That was an explicit selection of the first research envelope. 

For the diagonal-reference subfamily, the chosen birth quantity satisfies

$$
(BH_{\mathrm{ref}}B^\top)_{uv}
=
\sum_e w_e B_{ue}B_{ve}
=
0
$$

whenever \(u\) and \(v\) are nonadjacent. Hence its defined nonedge score is identically zero. ATC-2 records this result explicitly. 

No additional trajectory, more generous numerical precision, or positive threshold adjustment will make that particular quantity detect a nonedge coupling on that subfamily.

The correct conclusion is:

$$
\boxed{
\text{this witness at this selected read stage cannot supply OS edge birth}.
}
$$

It is **not**:

$$
\boxed{
\text{OS cannot support autonomous edge birth}.
}
$$

### K0 is a research choice that can receive a reviewed successor

My earlier insistence on not switching the OS stage was about preserving the meaning of the experiment. It must not become a prohibition against revising the scientific design.

We should not quietly change the read inside the existing ATC-2 experiment and call the resulting positive case evidence for the old law. But we absolutely can—and, for the intended functionality, should—investigate a successor.

That successor might define an operation-specific witness using other legitimate present-state OS structure. Alternatively, it might revise the ATC read contract so that the relevant OS geometry is reconstructed through an explicitly specified, non-writing computation.

Either route needs to establish exactly what is computed, what causal inputs it uses, which admission conditions it imposes, and how it relates to the underlying OS dynamics. It must not turn OS into CI, borrow a stale consumed current, or add a writer merely to obtain a nonzero score.

The important point is:

> **An accepted bounded research envelope protects the provenance of its results. It does not freeze an inadequate design forever.**

Thus the diagonal-reference null result should become the motivating negative result for the next witness/read investigation. It should not be used to justify shipping OS without the required operation.

## 4. The automatic dispatcher must be completed—but at the right stage

The dispatcher gap is different from the missing split law.

ATC-2’s research script generates requests and sends them to the existing supplied-event owner after a separate ordinary step. Its finite target catalogue and separate calls do not implement the integrated, serialized K0 after-beat mechanism. The proposal makes that distinction correctly. 

We should not demand that the final production dispatcher already exist before the investigation has supplied its accepted scientific contract. That is what 7T is for.

But there are two closure obligations:

**Before the specification is finalized**, the investigation must settle the dispatcher’s semantics: causal inputs, selected stage, complete policy identity, event construction, transaction composition, outcomes, target-policy transport and continued applicability after graph change. Research integration should pressure those semantics enough to expose architectural gaps.

**Before 7T closes and topology-dependent Tranche 8 begins**, the native dispatcher must actually implement and validate that contract.

This cannot remain “the application can call the generator and then call the event API.” That would leave the orchestration outside the substrate whose autonomy we are claiming.

The decisive execution should require only an initial admitted state, an enabled complete topology policy and ordinary evolution requests. The runtime must determine the event, construct its target, admit or reject it, preserve the correct publication, and remain able to evaluate the policy on the changed graph.

Save/load and duplication must preserve that ability. A later event must not depend on an external script reconstructing another finite target catalogue.

So, **yes: no native automatic dispatcher is an implementation blocker for completing 7T**. It is not necessarily a blocker for retaining ATC-2’s numerical research results.

## 5. There is a fourth gap: separate laws do not yet give one organism bidirectional topology dynamics

This deserves attention alongside your three examples.

ATC-2 deliberately tests birth and merge as **separate policies**, one selected law per experiment. It does not define cross-law resolution. 

That is useful for isolating and validating each proposal. But an organism that is permanently configured only to add edges is different from one that can both elaborate and simplify its structure as its state changes.

Similarly, a dispatcher that simply invokes whichever single law was configured does not answer:

> What happens when the current state supports both a refinement candidate and a coarsening candidate?

For the broader topology dynamics we intend, there must eventually be a **complete constitutive composition** of the required operations.

That does not mean introducing an external chooser. It means specifying the actual state-dependent law governing competing or compatible event prescriptions: whether they are mutually exclusive by construction, compared through a justified relation, combined when compatible, or left unresolved.

Neither a hard-coded “try split first” ordering nor a fallback to merge after a failed split should enter accidentally.

A single identity-bound composite policy could still fit the idea of “one complete law.” But its composition is new mathematics; it is not supplied by independently testing its components.

**Operation availability across profiles and operation composition within a run are both requirements.** Otherwise we could obtain nominal feature parity while still lacking the adaptive topology dynamics that motivated ATC.

## 6. “All ten” should become an explicit acceptance obligation

At present, the proposal records an applicability matrix with held, conditional, inactive and positively tested cells. That is the correct way to report an intermediate result. It is not necessarily an adequate final target. 

I would now distinguish three obligations.

### Common capability

For every required operation and candidate–realization family, the scientific construction must be defined on a nonempty, justified domain. A proven identically inactive witness does not satisfy this obligation for that operation.

The same formula need not work everywhere. But any realization-specific construction must be related to the common capability through explicit mathematical meaning—not merely through a shared API name.

### Native realization

The implementation must execute the complete path on admitted source and target profiles, including current/reset, history treatment, reference construction and subsequent ordinary evolution.

A successful read on a graph too small to perform the operation does not satisfy this obligation.

### Continued autonomous operation

The enabled law must survive its own graph change. The target must retain an admitted policy identity and the reference machinery needed to evaluate later events.

For the dynamical claim, the evidence should include ordinary evolution reaching an event condition, not only initialization inside an already active guard. ATC-2 explicitly says its three positive fixtures already satisfy their guards before the ordinary step. That is valid present-state generation evidence, but not onset evidence. 

This does not require identical trajectories across products or an unbounded-growth theorem. It requires a meaningful operational domain, a reproducible endogenous transition, discriminating negative controls and continued execution under the declared bounds.

## 7. We must not obtain parity by weakening the mathematics

Your completeness requirement should increase the research burden, not pressure the investigators to make every table cell green by changing the rules.

For example, the rejected A_PC source is a failure of one fixture under its fixed envelope, not proof that A_PC cannot support the operation. The next task is to derive and test a suitable admitted domain—or identify what exact successor contract is needed. It is not to enlarge the radius after observing the failure and describe that as the original result. 

Likewise, a classical Hessian cannot be asserted for a merely Lipschitz section to obtain the same analyzer everywhere. A source and target chart cannot be silently changed to make a split admit.

The distinction is:

$$
\boxed{
\text{common functional objective}
\neq
\text{forced mathematical equivalence}.
}
$$

If a genuine obstruction is eventually proved, it must trigger an explicit architectural decision: improve the proposed law, admit a justified substrate successor, or reconsider the advertised capability. It should not be hidden as “unsupported” while the aggregate generic-capability claim is marked complete.

That is not a promise that all current candidate laws will survive. **The laws are proposals; the functionality is the requirement.** A failed candidate is a reason to investigate a better construction, not automatically to delete the requirement.

## 8. How I would revise the next gate

I would retain the bounded ATC-2 results and change the forward recommendation from “synthesize the accepted subset now” to:

> **Adjudicate the sound partial results, but keep generic topology-capability closure open while resolving splitting, OS witness adequacy, cross-product applicability and complete operation composition.**

The division of work should be explicit:

| Outstanding issue                        | Required resolution                                                                                                           | Completion boundary                                                         |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Endogenous splitting                     | A complete source-to-partition law, construction and admission argument; profile-correct realization                          | Scientific extension scope before final specification; native closure in 7T |
| OS birth obstruction                     | A reviewed successor witness/read or another justified law providing the required capability                                  | Before claiming common cross-product birth capability                       |
| Incomplete all-product evidence          | Admitted source/target domains and end-to-end applicability for each required capability                                      | Research support before final scope; native conformance before 7T closes    |
| Separate birth/merge/refinement policies | A complete constitutive composition for the intended combined dynamics                                                        | Before specifying the combined ATC profile                                  |
| Native automatic execution               | Policy installation and transport, serialized composition, dynamic construction, persistence, rollback and repeated operation | 7T exit, before topology-dependent Tranche 8                                |

This does **not** require blocking all claim adjudication until everything is complete. Arithmetic, constructors and bounded negative results can receive their appropriate dispositions as they are earned.

What is needed is an **aggregate capability claim** whose dependencies remain open until the required functionality is complete. The existing origin claims and debt links should remain intact; the aggregate requirement should be added explicitly rather than retroactively pretending every original debt was always a universal blocker.

For example, the supplied index already distinguishes structural-trigger debts, native integration debts and all-product applicability debts. These can support the aggregate closure obligation without changing the meaning of earlier evidence. 

Not every open debt needs to become mandatory. Exact quotient preservation, universal attractor preservation or every proposed interpretation remain separate unless we claim them. But **endogenous splitting, a non-vacuous required operation set across the ten families, and native automatic execution are not optional interpretive refinements for the project you have described.**

## Revised recommendation

**Your objection is right at the program level.** We should not allow careful local disclaimers to turn an incomplete topology extension into the final design.

The appropriate disposition is:

$$
\boxed{
\text{ATC-2: retain and adjudicate its bounded results}.
}
$$

$$
\boxed{
\text{Generic topology functionality: not closed}.
}
$$

$$
\boxed{
\text{Next: resolve the capability gaps before final synthesis, then complete native execution in 7T}.
}
$$

The aim should be **the same required structural capabilities, realized faithfully through different candidate–realization dynamics**—not identical behavior, and not a permanently uneven feature matrix produced by whichever research fixtures happened to pass first.
