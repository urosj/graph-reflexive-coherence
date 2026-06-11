# N08 Implementation Notes

This directory tracks implementation work for
`2026-05-N08-lgrc-memory-trail-affordance`.

N08 starts after:

```text
N05:
    O5 self-sustained oscillator candidate;
    O6 route-coupled oscillator blocked by
    missing_route_conductance_memory_policy.

N06:
    SC6 artifact-only semantic route-choice candidate;
    memory/trail claims remain false.

N07:
    artifact-only, source-specific ID6 evidence classification for bounded
    non-destructive dual-basin exchange;
    runtime identity acceptance remains false.
```

N08 must keep the work experiment-local unless a separate Phase 8 task is
opened. Stop before changing `src/*`.

The first implementation goal is not a full ACO model. It is a clean
route-memory/trail evidence ladder:

```text
route-use event
-> memory surface
-> decay/reinforcement policy
-> memory-shaped route arbitration
-> artifact-only replay
```

All artifacts should be written under this experiment directory. Every positive
row must keep source artifacts, claim flags, budget evidence, and controls
explicit.
