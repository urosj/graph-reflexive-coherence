# N09 Implementation Notes

This directory tracks implementation work for
`2026-05-N09-lgrc-goal-proxy-regulation`.

N09 starts after:

```text
N05:
    O5 self_sustained_oscillator_candidate

N06:
    SC6 artifact_only_semantic_route_choice_candidate

N07:
    ID6 artifact-only source-specific bounded_non_destructive_exchange

N08:
    Hypothesis A:
        artifact_only_route_memory_or_trail_affordance_candidate

    Hypothesis B:
        static_positive_geometry_route_response_persistence_candidate
        blocker = native_route_conductance_memory_policy_missing
```

N09 must keep work experiment-local unless a separate Phase 8 task is opened.
Stop before changing `src/*`.

The implementation target is not agency or intention. It is a clean
goal-proxy regulation evidence ladder:

```text
runtime-visible proxy state
-> serialized target band
-> error signal
-> proxy-conditioned route or producer evidence
-> scheduled/processed packet work
-> proxy-state response
-> artifact-only replay
```

All artifacts should live under this experiment directory. Every positive row
must keep source artifacts, claim flags, budget evidence, producer boundaries,
and controls explicit.
