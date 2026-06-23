# Hypothesis B - Durable Geometry Replay And Re-entry

N22 can distinguish durable geometry modification from one-window flux
transients by showing that a susceptibility delta survives replay and later
re-entry without hidden producer reinforcement.

Support requires:

```text
susceptibility delta survives artifact replay
susceptibility delta survives snapshot/load replay
duplicate replay is stable where applicable
later route or region re-entry expresses the delta
interaction_delta_digest recorded
post_replay_delta_digest recorded
reentry_delta_digest recorded
delta_persistence_ratio recorded
delta_threshold_or_rule declared
one_window_transient_rejected = true
same-budget peer comparison rejects global drift or scheduler artifact
reinforcement schedule removed or neutralized control fails closed
one-window transient control fails closed
post-hoc delta stitching control fails closed
hidden producer support control fails closed
same-basin continuation remains inside declared floors
```

Failure conditions:

```text
delta disappears on replay
delta appears only during the interaction window
later re-entry is missing
delta digests do not match the declared persistence rule
delta persistence ratio falls below the declared threshold
same-budget peer route or region carries the same delta without demotion
producer reinforcement schedule carries the apparent modification
duplicate replay diverges without declared scope reason
support/coherence/boundary/flux floors are crossed
```
