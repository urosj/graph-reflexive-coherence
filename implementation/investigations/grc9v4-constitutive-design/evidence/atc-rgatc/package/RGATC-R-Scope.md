# RGATC-R — reference, conformance, and remaining authority

**Date:** 2026-09-24  
**Status:** bounded executable research reference, with internal positive/negative tests. Independent scientific review, source admission, and native implementation remain open.

## 1. What R adds

The reference now has an executed, error-certified invariant-section evaluator; a separate Decimal evaluator; full fixed-H Candidate-A read/writer comparison; coordinate covariance pressure; an atomic two-role research owner; physical replay; exact versus represented-state separation; and a finite binary64-publication bridge.

The physical completion and parameters are exactly those of T/A. Numerical refinement is separate: the physical profile identity binds the completion and coefficients, while each section certificate also binds its actual evaluator depth, inverse-work limit, and error tolerance. A deeper diagnostic query does not redefine the physical section.

The detailed finite-evaluator proof is in `RGATC-R-SectionEvaluator.md`. The actual outputs, signed intervals, counters, negative outcomes, and source hashes are retained in `RGATC-ER-Certificate.json`.

## 2. Complete ordinary and event staging

The ordinary read reconstructs Gamma from the current C/W state. That geometry supplies the one physical current. Continuity writes C once; the descriptor is rebuilt from the resulting C; the W writer uses the same current that drove continuity. A completely fresh section query at the new C/W state supplies poststate readmission.

The generated geometry from the consumed source is compared with that new section value. This checks the RG lagged invariance equation; it is not another physical geometry update or a same-beat corrector.

The source-only event is evaluated after an ordinary transaction has succeeded. Its selector reconstructs the poststate section/current. Current alone selects the dyadic share. Each actual role then receives its own C/W transfer and its own target section reconstruction. No H, Gamma, inverse iterate, or Z is transferred.

The owner publishes only after both target readmissions succeed. A reset restores the independently transported target reset C/W, not the most recent live C/W. Published intervals, states, and parameter mappings are immutable through their supported public interfaces.

## 3. Two transactions, two failure boundaries

The research dispatcher executes

\[
\text{ordinary commit}\quad\longrightarrow\quad
\text{source-only sufficient guard}\quad\longrightarrow\quad
\text{optional topology commit}.
\]

An ordinary failure preserves the preceding publication and cannot be rescued by a topology event. An event failure preserves the already completed ordinary publication. It does not roll the successful ordinary beat back. The failure suite exercises this distinction explicitly.

The split itself has zero duration. The ordinary beat advances the exact lifecycle clock by Delta. A no-event case executes its ordinary beat and then reports that the state is outside the sufficient event domain. That report is not a theorem that no other topology mechanism could apply.

Only one source fission is admitted by this bounded owner. Descendant fission and arbitrary event scheduling are not implemented.

## 4. Replay and proof interfaces

Replay starts from the exact admitted source roles and reexecutes each requested operation. Every action binds its before/after publication identity, and the final full snapshot must equal the reconstructed snapshot. Merely changing the final data and rehashing it does not make a forged record valid.

Negative pressure includes missing source lineage, changed frozen duration, forged profile, forged reset history, wrong edge lineage, forged selected-section identity, nonzero event duration, late publication exceptions, ordinary final-readmission failure, and reset readmission failure after current has succeeded.

Exact rational input constructors check charge and pairing before outward-grid conversion. Only executing physical operations can construct operation-derived states. Passing raw output or a serialized object as a request does not mint authority. The public transfer interface has no geometry-transport argument.

This is a mathematical/API conformance boundary, not protection against hostile code that can replace modules, call private constructors, or bypass Python immutability deliberately. Native lifecycle security and production authorization are separate work.

## 5. Exact boundaries and the auxiliary completion

The test suite includes exact W-floor inputs, the exact source root-corridor endpoint, offsets of size 2^-300 outside the admitted exact predicates, broken pairing at sub-grid scale, and an exact charge forgery at sub-grid scale. Those decisions use rational input facts rather than tolerances.

The finite section algorithm is also pressured with insufficient graph-transform depth, an exhausted inverse budget, and a query box too wide for its requested error. These cases must fail even if an approximate numerical answer looks plausible.

Auxiliary tests include a support-transition point with negative C and active conductance floor, and a point outside support with nonpositive W. The latter must return the identity/reference completion without evaluating log(W). Neither auxiliary case is admitted as a physical state. A separate positive source extremely close to zero produces an actually negative physical proposal, which is rejected before the physical W writer.

The exact mathematical completion is global. The finite evaluator is a fail-closed certified subset. This package does not claim executable success at every theoretical domain point or at arbitrarily fine boundaries under a fixed arithmetic/work budget.

## 6. Coordinate covariance

The reference and the separate Decimal evaluator execute a nontrivial vertex permutation, edge reorder, and orientation reversal of the paired target. C and W use their unsigned coordinate actions; J uses the signed edge action; H and S use signed congruence. Selected and fresh poststate sections, currents, structural sources, and resulting C/W are compared.

This is one complete executable representation check, backed by the analytic equivariance theorem in T/A. It is not a numerical campaign over every labeling and not arbitrary-graph admission. The research owner uses the fixed canonical paired source and target.

## 7. Finite represented-number bridge

Each actual target role is advanced through four requests, all equal to the one frozen dyadic Delta. C/W is projected to binary64 only at publication, and each subsequent step starts from the preceding rounded publication. A projection succeeds only when both endpoints of its enclosure round to the same binary64 value.

The section is reconstructed afresh for the represented point. Geometry is not a serialized numerical history coordinate. The section evaluator still targets the **original exact physical tau**. The ordinary numerical writer uses the binary64 approximation of tau. These are numerical errors relative to the same frozen mathematical profile, not a switch to a new section defined by tau64.

A separate local bridge makes that distinction quantitative. Let \(\bar X\) be the represented input, \(F(\bar X,\Gamma(\bar X))\) the exact-profile proposal, and \(\bar X^+\) the rounded result from the approximate writer. The interval calculation supplies

\[
e_X\ge\|\bar X^+-F(\bar X,\Gamma(\bar X))\|_\infty.
\]

Because the physical-agreement cutoff is one here, exact RG invariance and section Lipschitz continuity imply

\[
\boxed{
\|\Gamma(\bar X^+)-G(\bar X,\Gamma(\bar X))\|_F\le L e_X.
}
\]

Equivalently, with \(Y=F(\bar X,\Gamma(\bar X))\), the same bound is simply

\[
\|\Gamma(\bar X^+)-\Gamma(Y)\|_F\le L e_X.
\]

The code retains this bound and checks consistency of the independently computed geometry centers after adding their certified section/arithmetic errors. Thus the represented path does not falsely claim zero exact RG invariance residual after rounding.

The four-step shadow comparison bounds C, W, J, and reconstructed H errors by 10^-10. It retains hexadecimal publications, the exact represented tau, and exact rational charge drift. Represented roots carry no exact-charge-nine authority; a deliberately non-Q9 represented state remains a diagnostic point rather than being promoted into the return theorem.

This is not an all-binary64 internal solver, an indefinite numerical theorem, exact numerical charge conservation, or a practical performance result at a larger beat/gain. In particular, the small genuine geometry increments in this profile are evaluated at high precision; behavior of a production solver that rounds H itself requires separate evidence.

## 8. Disposition

The attained scope is:

* RGATC-E: an actually executed section-based onset, source-only selector, both-role fission and reconstruction, finite target continuation, and finite no-split/history-reset controls.
* RGATC-R: the bounded finite section/error bridge, independent numerical checks, exact/auxiliary boundary pressure, one full coordinate transform, research lifecycle/replay/failure tests, and four-step represented shadowing with a local RG-defect bound.

The following remain open and are not silently converted into implementation chores already completed: independent review of T/A and this package; formal profile and source admission; native Candidate-A potential/completion support; production current/section/clock/rounding/transaction conformance; an indefinite numerical guarantee; practical larger parameter domains; active external environments; repeated autonomous events/non-Zeno claims; and aggregate ATC-2 closure.

No origin or realization-local debt ledger is modified. A separate scoped adjudication must decide which obligations the internally produced evidence actually supports.
