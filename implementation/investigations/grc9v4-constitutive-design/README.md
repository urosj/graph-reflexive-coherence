# GRC9V4 Constitutive Design Investigation

**Disposition:** Active pre-specification investigation

This directory owns the decision work required before a normative GRC9V4
specification can be written. It consumes the Continuation/Read-Back 3.4.1
theory-to-graph contract, the accepted B1-GR and B2-GR boundaries, the
reconciled legacy GRC9V3 specification, and the Phase 7 implementation record.
This is also the historical chain that produced the V4 question. B1 made the
theory distinctions executable against unchanged GRC9V3; B2 tested stronger
unchanged-runtime constructibility. Their bounded results constrain this work
but do not prescribe a V4 architecture.

The investigation does not assume that GRC9V4 is temporalized conductance,
introduces a new independent retained carrier, or temporalizes current. D1
admits retained-representation ontologies; D6 separately decides whether
current remains slaved. Final architecture selection belongs only to D10. The
investigation compares the admitted candidates against one frozen target:

> GRC9V4 is a possible revision-distinct synchronous GRC profile in which an
> admitted retained causal representation participates in structurally and
> temporally classified continuation and is conditionally read by present
> activity into an oriented current contribution.

D0-D3 are the verification-to-design bridge. From D4 onward, B1/B2 provide
bounded V3 facts, verification controls, design pressure, and open hypotheses;
they do not dictate V4 ontology. Their conclusions should not be rerun merely
to rediscover V3, but must be revisited when V4 changes the causal object,
state space, or operator. Every gate must add a candidate-specific constitutive
fact, reject a candidate for a named incompatibility, or route a named missing
derivation.

Start with:

- [constitutive design basis](./GRC9V4ConstitutiveDesignBasis.md);
- [D0-D10 investigation plan](./GRC9V4ConstitutiveDesignPlan.md);
- [execution checklist](./GRC9V4ConstitutiveDesignChecklist.md);
- [decision ledger](./GRC9V4ConstitutiveDesignDecisionLedger.md);
- [frozen initialization predecessor](./GRC9V4ConstitutiveDesignInitialization.json);
- [D0 structured decision](./decisions/D0TargetInheritanceAndClaimCeiling.json);
- [D0 interpretation](./decisions/D0TargetInheritanceAndClaimCeiling.md).
- [D1 structured decision](./decisions/D1RetainedRepresentationOntologyAndCandidateAdmission.json);
- [D1 interpretation](./decisions/D1RetainedRepresentationOntologyAndCandidateAdmission.md).
- [D2 structured decision](./decisions/D2FormationRetentionReleaseAndWriteInterface.json);
- [D2 interpretation](./decisions/D2FormationRetentionReleaseAndWriteInterface.md).
- [D3 structured decision](./decisions/D3ContinuationRequirementsAndStructuralDomain.json);
- [D3 interpretation](./decisions/D3ContinuationRequirementsAndStructuralDomain.md).
- [D4 structured decision](./decisions/D4GeometryMobilityAndTopologyOwnership.json);
- [D4 interpretation](./decisions/D4GeometryMobilityAndTopologyOwnership.md).
- [D5 structured decision](./decisions/D5DirectionalReadBack.json);
- [D5 interpretation](./decisions/D5DirectionalReadBack.md).
- [D6 structured decision](./decisions/D6TotalCurrentClosure.json);
- [D6 interpretation](./decisions/D6TotalCurrentClosure.md).
- [D7 structured decision](./decisions/D7ClosedWriteReadLoop.json);
- [D7 interpretation](./decisions/D7ClosedWriteReadLoop.md).

Current gate status:

```text
D0 = accepted
D1 = accepted_bounded
D2 = accepted_bounded
D3 = accepted_bounded
D4 = accepted_bounded
D5 = accepted_bounded
D6 = accepted_bounded
D7 = accepted_bounded
D8 = authorization_deferred_pending_separate_human_direction
```

D5 currently defines two bounded candidate operator channels (A and C), routes
B to a named derivation, and physically identifies zero channels. Its 68-point
hardening audit keeps trial current distinct from the D6 total-current solve and
keeps A/mobility attribution plus C/`T_C` mediation explicitly open. Typed
operator-family admission is separate from closed retained mediation, all D4
debts have explicit successor dispositions, and pre-spec design obligations are
separated from post-spec causal verification. B remains an architecture
candidate while routed out of D6; it has not been eliminated.

D6 now selects bounded same-beat algebraic slaving for A and parameterized C
and keeps B routed without rejection. The declared solve freezes all noncurrent
context, making `zeta chi R` the complete within-solve block only for that
revision-distinct lagged-geometry staging, not for the core simultaneous loop
in general. Loss of invertibility fails closed; it does not establish a temporal
current law, fast-limit interpretation, stability threshold, write-back, or a
closed reflexive loop. Its 96-point hardening audit also separates partial
deslavement, solver behavior, admissible current support, harmonic topology,
shared current/geometry gain, and mathematical absorbability from those later
claims. Postsolve `J_C` is D7's authoritative causal current; diagnostic `j`
cannot bypass it as a direct write input. Transitive debt persistence keeps 20
older unresolved IDs, including 16 pre-D10 blockers, visible beside the 25
current debts. D6 was accepted bounded on 2026-08-24; D7 has now been executed
and awaits human review.

D7 now defines one complete Candidate A fixed-stratum kinetic reduced
transition. Authoritative `W_A` drives the graph baseline, the accepted D5/D6
edge-contrast operator closes total current, and the exact downstream mediator
`D_A[k] = (C[k+1], J_C_A[k])` writes one bounded positive `W_A[k+1]` through a
log-geometric one-beat update. This closes the direct retained-mobility
recurrence. The explicit Read-Back subloop is separately constitutively
load-bearing on its declared nondegenerate domain; exact physical
nonabsorbability remains open.
It does not close the normative structural path: `K_4 -> H_4 -> h_4` remains
underdefined, so structural cultivation and a complete GRC9V4 architecture are
still unsupported. B and C remain routed, not rejected. D7 is accepted bounded;
D8 remains unauthorized pending a separate human direction, with eligible
scope limited to A's concrete reduced transition and its explicit structural
boundary. The original 72-row pressure audit and an additional 96-row
adversarial audit preserve these distinctions item by item.
The explicit `J_C squared` writer term is sign-even, but full physical history
reversal may change continuity-mediated `C[k+1]` and therefore the complete A
writer; scalar state is not relabeled as signed cochain memory. D7 also freezes
a three-way D10 debt union, with named pre-D10 audits required for A's
core-status, absorbability, and units/gauge questions. Reduced temporal
stability is a D8 question; normative structural stability remains blocked on
the missing `H_4` map.
The later specification and implementation must also rebuild every
differential or gradient summary used by `G_W(C[k+1], J_C[k])` from
post-continuity `C[k+1]`; pre-continuity cache reuse is outside the accepted
writer contract.

Hard boundary:

```text
D0-D10 accepted design closeout
  -> may authorize a separate normative GRC9V4 specification tranche

anything earlier
  -> no grc-9-v4-spec.md
  -> no src/ changes
  -> no GRC9V4 capability claim
```

The current design tranche may close unresolved without selecting an
architecture, but that does not reject the GRC9V4 target. Candidate exhaustion
must localize the missing role and route named theory, constitutive,
candidate-admission, or discriminator work. That is preferable to encoding a
convenient memory field that the theory and evidence do not justify.
