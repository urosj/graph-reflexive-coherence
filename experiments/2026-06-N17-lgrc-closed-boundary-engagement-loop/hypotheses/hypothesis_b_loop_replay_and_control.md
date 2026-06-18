# Hypothesis B - Loop Replay And Control

## Claim

The loop remains valid under replay and order controls; it is not created by
post-hoc labeling, hidden state injection, hidden state carryover, or
hand-authored causal narration.

## Required Evidence

```text
artifact-only replay stable
snapshot/load replay stable
duplicate replay stable
order-inversion control fails closed
one-way crossing relabel control fails closed
post-hoc loop stitching control fails closed
feedback-removed control fails closed
hidden state carryover controls fail closed
```

## Boundary

This supports only control-clean artifact-level loop closure. It does not
convert a one-way boundary crossing trace into a closed loop unless ordered
external-internal-external-later-internal dependence is present. If the later
external feedback state is removed or frozen, the closed-loop claim must fail
closed.
