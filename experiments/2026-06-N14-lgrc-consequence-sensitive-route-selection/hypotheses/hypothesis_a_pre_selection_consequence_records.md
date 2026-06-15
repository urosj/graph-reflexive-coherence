# Hypothesis A - Pre-Selection Consequence Records

## Statement

```text
Route candidates can be annotated with source-backed, pre-selection
consequence records over support, memory, and regulation surfaces without
using hidden outcome tables or post-hoc consequence scoring.
```

## N14-Specific Meaning

This hypothesis is about the evidence surface needed before consequence-
sensitive route selection can be evaluated. N14 must show that candidate routes
carry downstream effect descriptors before selection occurs.

The descriptors must be artifact-visible and source-backed:

```text
expected_support_effect
expected_memory_effect
expected_regulation_effect
bounded_consequence_horizon
budget_cost_surface
prediction_basis
derivation_policy
source_window
observed_downstream_effect
prediction_match_status
source_artifact_digest
record_timing = pre_selection
```

This is not a claim that the system understands consequences. It is not a
claim that the system owns a goal or intends an outcome.

## Acceptance Requirements

Hypothesis A can be supported only if:

```text
each route candidate has a consequence record
each consequence record is source-backed
each consequence record is serialized before selection
each consequence record states its prediction basis and derivation policy
each consequence record pins its source window
support, memory, and regulation fields are explicit or explicitly absent
observed downstream effects and prediction match status are recorded when the
bounded horizon is evaluated
hidden outcome table controls fail closed
post-hoc consequence scoring controls fail closed
stale consequence record policy is defined
claim flags remain false
```

## Rejection Conditions

Reject or defer the hypothesis if:

```text
route ranking depends on a hidden outcome label
consequence records are created after the selected route is known
downstream effects are unpinned prose labels
budget costs are missing
source artifacts are missing or unpinned
semantic intention or agency language is required to explain the record
```

## Claim Boundary

```text
pre-selection consequence record != intention
expected downstream effect != semantic goal ownership
support-effect descriptor != identity acceptance
artifact consequence record != native support
```
