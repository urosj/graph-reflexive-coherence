# Implementation Trace

This directory records what is done for the
`2026-05-N06-lgrc-semantic-route-choice` experiment family and why.

N06 starts after N05 closed at:

```text
strongest_supported_o_level = O5
strongest_claim_ceiling = self_sustained_oscillator_candidate
o6_route_coupled_oscillator_supported = false
```

N06 does not continue oscillator, memory, trail, or ACO claims directly. It
opens a route-choice question:

```text
Can LGRC select among competing routes because of serialized runtime-visible
context or affordance evidence?
```

Use this area for experiment-local notes such as:

- SC-ladder run plans,
- candidate-route fixture design,
- context/affordance surface definitions,
- native route-arbitration controls,
- hidden-input and preselected-sink blockers,
- artifact-only replay reports,
- and closeouts.

This is not the global `implementation/` directory. If N06 discovers missing
native support for context surfaces, affordance maps, compatibility gates, or
selection replay, stop and open a separate Phase 8 implementation task.

## Claim Boundary

N06 may produce semantic route-choice candidates. It must keep these blocked
unless separately validated in later experiments:

```text
memory or trail formation
agency
agentic-like behavior
RC identity collapse
identity acceptance
locomotion-like behavior
biological behavior
ant-colony behavior
unrestricted movement
```

Native route arbitration alone is not semantic choice. It becomes N06 evidence
only when selection is explained by runtime-visible context or affordance
relations and replayed from artifacts.

## Current Status

Initial definition only. No N06 probes have been run yet.

Start with the root experiment README:

```text
../README.md
```

Then use:

```text
SemanticRouteChoiceImplementationPlan.md
SemanticRouteChoiceImplementationChecklist.md
```
