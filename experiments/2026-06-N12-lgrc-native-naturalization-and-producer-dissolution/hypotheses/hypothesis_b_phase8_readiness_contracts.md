# Hypothesis B: Native Policy Surface Candidates

Hypothesis B states that some mechanisms can be naturalized as native LGRC
policy surfaces without adding non-RC quantities.

## Question

```text
Can selected producer-layer mechanisms be specified as RC-compatible native
LGRC policy-surface candidates with runtime-visible surfaces, serialized
thresholds, separated budgets, telemetry requirements, test gates, and
fail-closed controls?
```

## Likely Candidates

```text
native_route_conductance_memory_policy
native_response_magnitude_policy
```

## RC Compatibility Requirements

```text
RC causality preserved
coherence accounting preserved
LGRC geometry preserved
packet scheduling preserved
topology lineage preserved
budget conservation preserved
no non-RC quantities introduced
```

## Required Controls

```text
native support claimed without Phase 8 source -> blocked
route conductance memory relabeled as intention, ACO, or ant-colony behavior -> blocked
response magnitude relabeled as intention or goal ownership -> blocked
hidden producer mutation -> blocked
stale source replay -> blocked
budget discontinuity -> blocked
```

## Expected Conservative Result

```text
NAT4 Phase 8 readiness may be supported for concrete rows
Phase 8 implementation remains unopened
native support remains false until separate implementation and validators exist
```
