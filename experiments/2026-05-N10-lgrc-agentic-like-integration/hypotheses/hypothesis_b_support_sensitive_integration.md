# Hypothesis B: Support-Sensitive Integration

Integration is valid only while the identity/support baseline is still valid,
or after explicit restoration evidence.

## Question

```text
Does a route-memory-regulation composition remain valid only when the
identity/support baseline survives, and does it block or downgrade when support
is disrupted?
```

## Expected Useful Outcomes

```text
support_intact_survives -> integration may proceed
mild_withdrawal_survives -> integration may proceed if source-backed
n09_matched_withdrawal_disrupts_support -> integration blocks or downgrades
explicit_restoration_recovers_support -> integration may resume after
    restoration evidence
```

## Required Evidence

```text
N07 Iteration 13 support-intact lane
N07 Iteration 13 mild-withdrawal lane
N07 Iteration 13 N09-matched withdrawal lane
N07 Iteration 13 explicit-restoration lane
N09 regulation source artifact
integration rows or blocked rows for each support state
artifact-only replay
claim flags false
```

## Required Controls

```text
stale identity/support baseline -> blocked
support disrupted but integration accepted -> blocked
restoration required but missing -> blocked
hidden restoration -> blocked
support history erased -> blocked
identity acceptance claim promotion -> blocked
agency claim promotion -> blocked
```

## Interpretation

This hypothesis protects N10 from treating regulation as integrated when the
support identity baseline has failed. A disrupted-support block is a positive
safety result, not a failed experiment.

## Non-Claims

Hypothesis B does not support:

```text
identity acceptance
identity ownership
agency
intention
personhood
unrestricted identity continuity
```

## N10 Iteration Link

Hypothesis B is introduced by Iterations 3, 4, 5, 6, and 9, then tested at the
full-composition boundary by Iterations 10, 11, and 12.

## Post-Hypothesis-A Continuation

Iteration 9 closes the bounded artifact-only Hypothesis A path. The remaining
Hypothesis B question is stricter:

```text
Does the full route-memory-support-regulation composition behave correctly
across support states?
```

The expected matrix is:

```text
support_intact_survives:
    full composition may proceed

mild_withdrawal_survives:
    full composition may proceed under the bounded companion scope

n09_matched_withdrawal_disrupts_support:
    full composition must block or downgrade

explicit_restoration_recovers_support:
    full composition may resume only through explicit restoration evidence
```

The useful result is not that every support state passes. The useful result is
that N10 does not accept the full composition when the identity/support
baseline has been disrupted.

Current continuation state:

```text
Iteration 10 passed:
    attempted full A6/ALI6 composition under N07 N09-matched disrupted support
    accepted no A6/ALI6 row
    preserved route, memory, regulation, support, and Hypothesis A source links
    primary blocker = support_disrupted_but_integration_allowed

Iteration 11 passed:
    explicit restoration resumed the full composition as
    restoration_gated_integration_candidate
    accepted A6/ALI6 under the restored support lane
    preserved the Iteration 10 disrupted-support record
    did not open A7/generalization, agency, or identity-acceptance claims

Iteration 12 passed:
    closed the support-state matrix
    hypothesis_b_status =
        supported_bounded_support_sensitive_full_composition
    support_intact_survives preserved bounded composition
    mild_withdrawal_survives preserved the bounded companion scope
    n09_matched_withdrawal_disrupts_support blocked attempted A6/ALI6
    explicit_restoration_recovers_support resumed A6/ALI6 through explicit
        restoration evidence
    preserved artifact-only replay, exact budget checks, source digests, and
        false claim flags
```

## Closeout State

Hypothesis B is closed for the bounded N10 scope:

```text
hypothesis_b_status = supported_bounded_support_sensitive_full_composition
positive_scope = bounded_artifact_only_support_sensitive_full_composition
artifact_only = true
runtime_state_used = false
```

This means the composition is support-sensitive, not unconditional. The full
composition remains acceptable under intact and mild support, blocks under the
N09-matched disrupted-support lane, and resumes only after explicit
restoration evidence. The disrupted-support block remains a positive safety
result.

Why this hypothesis was needed:

```text
Hypothesis A proved that the route-memory-support-regulation chain can be
composed in a bounded artifact-only window.

Hypothesis B tests whether that composition remains dependent on the
identity/support prerequisite.
```

Without Hypothesis B, the Hypothesis A positive row could be overread as an
unconditional composition. The support-state matrix prevents that by requiring
the composition to follow the support state:

```text
intact support:
    preserves the bounded composition

mild withdrawal:
    preserves the bounded companion scope

disrupted support:
    blocks attempted A6/ALI6 with
    support_disrupted_but_integration_allowed

explicit restoration:
    resumes A6/ALI6 as restoration_gated_integration_candidate
```

What Hypothesis B proved:

```text
The N10 composition is bounded and support-sensitive. It can proceed while
support is valid, must block when support is disrupted, and may resume only
after explicit source-backed restoration. This is evidence for a clean
integration boundary, not evidence for agency or identity acceptance.
```

Carry-forward boundary:

```text
Hypothesis B does not open A7/generalization, fully native agentic-like
integration, agency, semantic goal ownership, identity acceptance, RC identity
collapse, ACO, biological, personhood, or unrestricted agency claims.
```
