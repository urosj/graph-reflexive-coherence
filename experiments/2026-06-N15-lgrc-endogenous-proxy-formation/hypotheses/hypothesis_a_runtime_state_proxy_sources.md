# Hypothesis A - Runtime-State Proxy Sources

## Statement

```text
Runtime-visible support, memory, regulation, or support/identity-condition
state can be inventoried as a bounded source surface for proxy formation
without accepting externally supplied target conditions.
```

## N15-Specific Meaning

This hypothesis is about the evidence surface needed before endogenous proxy
formation can be evaluated. N15 must show that target formation has
artifact-visible source state available before a proxy is generated.

The source state must be artifact-visible and source-backed:

```text
evidence_strategy
old_best_claim_inputs
direct_historic_support_status
support_state_descriptor
identity_condition_descriptor
memory_state_descriptor
regulation_state_descriptor
state_source_window
source_current
source_sha256
source_report_sha256
budget_cost_surface
budget_units
declared_proxy_absent
external_target_input_absent
```

This is not a claim that the system accepts an identity. It is not a claim that
the system understands, owns, or semantically chooses a goal.

## Acceptance Requirements

Hypothesis A can be supported only if:

```text
each runtime-visible state input is source-backed
each state input pins its source artifact and source window
direct historic proxy-formation support is used when present and claim-clean
old best claim inputs are recorded when the candidate is constructed
state inputs are current under the experiment freshness policy
support, memory, regulation, and support/identity-condition fields are explicit
or explicitly absent
external target input absence is recorded before proxy derivation
declared proxy fixtures are excluded from the endogenous source surface
budget costs and budget units are recorded for the state surface
hidden target derivation controls fail closed
source inventory can be reconstructed from serialized artifact references
claim flags remain false
```

## Rejection Conditions

Reject or defer the hypothesis if:

```text
target formation depends on an unpinned state label
source state is stale or unavailable
the experiment provides the target condition before derivation
an old claim ceiling is exceeded during source inventory
support/identity-condition descriptors are promoted into identity acceptance
budget costs are missing or ambiguous
semantic goal ownership or agency language is required to explain the source
```

## Claim Boundary

```text
runtime-visible source state != semantic goal ownership
support/identity-condition descriptor != identity acceptance
source-current support state != agency
artifact state inventory != native support
```
