# Prototype D I14.4-4 Producer-Mediated Directed Cycle Bridge

Status: `passed`

Acceptance state: `accepted_producer_mediated_directed_cycle_bridge_candidate_pending_i14d_i14e`

Output digest: `44fe1547a6abd4313dc4ffff1da3f351e82f73c8f74ac569bce024b517ba45d8`

## Summary

```text
producer_mediated_directed_cycle_candidate_created = true
native_directed_cycle_supported = false
all_legs_locally_forward = true
reverse_bounce_back_used = false
sign_inverted_reverse_leg_used = false
ready_for_i14d_i14e = true
ready_for_iteration_15 = false
```

## Geometry

I14.4-4 resolves the I14.4-3 native blocker only in the N29 producer-mediated bridge lane. The first leg is the source-current I4-F neutral circulation: alpha enriches beta while beta drains against a near-stable buffer. The second leg does not bounce back along the same channel. It shifts frame and continues forward from beta toward gamma, consuming the changed medium left by the first leg. Closure is recorded because the later alpha-class state depends on the second leg's changed distribution. This is a directed-cycle bridge candidate, not native LGRC closed circulation.

The difference from I14.4-1 is important: I14.4-4 does not create an
opposite-direction return leg. It creates a frame-shifted second forward
leg. The loop is Escher-stairs-like: every local leg proceeds forward in
its own frame, while the ordered dependency closes at the pattern-class
level.

## Claim Boundary

Claim ceiling: `producer_mediated_all_forward_directed_cycle_candidate_pending_controls_replay`

I14.4-4 resolves I14.4-3 only as a producer-mediated bridge candidate.
It does not upgrade native LGRC directed-cycle support and it does not
open resource economy, cooperation, exploitation, ecology success, or
agency claims.

## Remaining Debt

- I14-D loop/composition controls pending
- I14-E replay/stress pending
- second forward leg is producer-mediated, not native LGRC source-current
- I14.4-3 native directed-cycle blocker remains in force
- resource economy, cooperation, exploitation, ecology success, and agency claims remain blocked

## Checks

| Check | Passed |
|---|---:|
| `i14_4_3_native_directed_cycle_absent` | `true` |
| `source_current_first_leg_present` | `true` |
| `all_legs_locally_forward` | `true` |
| `reverse_bounce_back_not_used` | `true` |
| `sign_inverted_reverse_leg_not_used` | `true` |
| `second_leg_consumes_prior_changed_medium` | `true` |
| `later_state_returns_to_starting_pattern_class` | `true` |
| `forward_magnitude_gate_passed` | `true` |
| `closure_residual_gate_passed` | `true` |
| `merge_leakage_gate_passed` | `true` |
| `native_directed_cycle_blocked` | `true` |
| `artifact_manifest_sha_match` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
