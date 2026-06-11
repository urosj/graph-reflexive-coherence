# Canonical Column-H Lane Decision

Date: 2026-05-05

Related readiness track:

- [GRC9V3-Hessian-ImplementationPlan.md](./GRC9V3-Hessian-ImplementationPlan.md)
- [GRC9V3-Hessian-ImplementationChecklist.md](./GRC9V3-Hessian-ImplementationChecklist.md)

## Decision

Lane B was not in scope for the GRC9V3 Hessian / Hybrid Spark Implementation
Readiness pass.

Lane B is deferred, not rejected.

## Scope

This pass remains focused on Lane A:

```text
current_hybrid_signed_hessian
```

## Reason

The current goal is to freeze, audit, test, and harden the existing `GRC9V3`
Hessian / hybrid spark runtime, not to introduce a new spark predicate.

Lane A is the object under test for the current GRC9V3 property experiments.
Changing spark semantics now would blur implementation readiness with
theory-completion and would weaken the baseline comparison value.

## Consequence

Column-H / cancellation evidence remains derived in Lane A.

Reports must not claim direct column-H spark gating under Lane A. Direct
column-H proxy-branch gate evidence belongs only to explicit Lane B runs.

Lane C comparison was deferred during readiness because there was no Lane B
runtime to compare against yet.

## Future

Lane B may be opened later as a separate repo-level implementation task with
its own:

- explicit config mode,
- predicate semantics,
- positive and negative tests,
- direct artifact fields,
- telemetry/checkpoint evidence,
- and Lane A / Lane B comparison plan.

## Post-Decision Update

Lane B v1 has now been opened as that separate repo-level implementation task:

- [GRC9V3-CanonicalColumnH-ImplementationPlan.md](./GRC9V3-CanonicalColumnH-ImplementationPlan.md)
- [GRC9V3-CanonicalColumnH-ImplementationChecklist.md](./GRC9V3-CanonicalColumnH-ImplementationChecklist.md)

The implementation lane id is:

```text
grc9v3_column_h_assisted
```

The phrase `canonical_column_h` remains the conceptual core GRC9 column-H
diagnostic source. It is not the GRC9V3 runtime lane id.

This update does not retroactively change the readiness decision. Lane A
artifacts remain `current_hybrid_signed_hessian` artifacts, and direct column-H
proxy-branch gate evidence is valid only for explicit Lane B runs.
