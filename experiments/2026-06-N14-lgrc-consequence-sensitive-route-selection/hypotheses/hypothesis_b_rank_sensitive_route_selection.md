# Hypothesis B - Rank-Sensitive Route Selection

## Statement

```text
Route selection can be classified as consequence-sensitive when the selected
route changes with recorded downstream support, memory, or regulation effects
under replayable budget constraints, rather than immediate affordance or
fixture labels alone.
```

## N14-Specific Meaning

This hypothesis is about the AP4 transition. It requires more than attaching a
consequence record to each route. N14 must show that the selection result is
sensitive to the downstream effect vector and not merely to immediate
affordance, route labels, fixture ordering, or producer preference.

The expected selection surface is:

```text
candidate_routes
eligible_candidate_set
pre_selection_consequence_records
immediate_affordance_rank
consequence_rank
selected_rank
budget_validity
bounded_consequence_horizon
deterministic_selection_rule
tie_policy
selected_route
selection_rationale_surface
```

## Acceptance Requirements

Hypothesis B can be supported only if:

```text
selection is replayable and deterministic for the same inputs
all eligible route candidates in the bounded window are represented
missing consequence records are rejected
selected route is budget-valid
selected route depends on downstream support, memory, or regulation effects
at least one matched or conflicting immediate-affordance case is resolved by
the consequence vector
rank order can change when consequence records change under controlled variants
immediate-affordance-only controls fail closed
fixture-label preference controls fail closed
post-hoc scoring controls fail closed
stale consequence records are rejected or marked unsupported
```

## Rejection Conditions

Reject or defer the hypothesis if:

```text
selected route is explained only by immediate route affordance
selected route is explained only by a fixture label
candidate set excludes eligible rejected routes
selection uses consequence data unavailable before selection
selection chooses a budget-invalid route
selection silently accepts a missing consequence record
rank changes cannot be replayed from serialized inputs
producer code mutates state directly instead of recording/scheduling selection
```

## Claim Boundary

```text
rank-sensitive route selection != intention
support-preserving route choice != agency
memory-sensitive route choice != identity acceptance
regulation-sensitive route choice != goal ownership
artifact-level AP4 != native support
```
