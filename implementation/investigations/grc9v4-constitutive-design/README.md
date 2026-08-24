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

Current gate status:

```text
D0 = accepted
D1 = accepted_bounded
D2 = open_not_yet_executed
```

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
