# Prototype D I14.4-3 Native Directed Circulation Cycle Search

Status: `passed`

Acceptance state: `accepted_native_directed_cycle_absent_broader_loop_definition_recorded`

Output digest: `6c0ef71941c7e5ccf4ca39702cb1956a32aaf772cffb7bd04181cdb70af24eee`

## Summary

```text
native_directed_cycle_found = false
native_closed_environmental_circulation_supported = false
producer_fallback_used = false
ready_for_i14d_i14e = false
```

## Difference From I14.4-2

I14.4-2 searched for an opposite-orientation reverse leg. I14.4-3 uses the broader loop definition: all legs may point forward, as long as their ordered dependencies close back to the starting pattern class.

A loop can be a directed cycle, not a bounce-back. It can move forward
from one pattern to another and then forward again into a later state
that closes dependency back to the starting pattern class. I14.4-3
therefore does not require sign-inverted opposite orientation.

## Interpretation

Under this broader loop definition, the native result is still negative
for the current source set. Native neutral-circulation rows exist, but
none records a later source-current leg that consumes the I4-F changed
medium and returns dependency to the starting pattern class.

Blocked reason: Native neutral-circulation rows exist, but none records a later forward leg that consumes the I4-F changed medium and returns dependency to the starting pattern class.

## Remaining Debt

- native LGRC needs ordered multi-leg circulation telemetry over changed medium states
- I14.4-1 remains a producer-mediated bridge candidate for how closure could work
- a future native directed cycle need not be opposite-orientation, but it must be source-current and dependency-closed

## Checks

| Check | Passed |
|---|---:|
| `broader_loop_definition_recorded` | `true` |
| `native_forward_leg_found` | `true` |
| `producer_fallback_not_used` | `true` |
| `native_directed_cycle_absent` | `true` |
| `native_closed_loop_blocked` | `true` |
| `unsafe_claim_flags_false` | `true` |
| `no_absolute_paths_in_records` | `true` |
