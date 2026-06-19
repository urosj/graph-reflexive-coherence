# Hypothesis B - Phase 8-Ready Contract Candidates

Some N13-N18 components can be specified as native contract candidates or
Phase 8-ready native policy candidates.

This can only pass where the candidate records:

```text
native policy or telemetry surface name
runtime-visible inputs
state mutation owner
record schema sketch
default-off flags
enabled / validated / supported separation
budget surface
telemetry requirements
snapshot/replay requirements
negative controls
non-RC quantity audit
claim flags forced false
src_diff_empty = true
phase8_opened = false
native_support_opened = false
```

Failure condition:

```text
a row reaches NAT4 without explicit runtime inputs, mutation boundary,
telemetry, replay, controls, budget, or claim-boundary gates
```

