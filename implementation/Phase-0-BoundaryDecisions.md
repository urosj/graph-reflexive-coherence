# Phase 0 Boundary Decisions

This document records the implementation boundaries that were already decided by the specs and Phase 0 planning work.

Its purpose is practical:

- later phases should not need to reconstruct these choices from multiple spec files,
- baseline implementation defaults should not drift by accident,
- and family differences should remain explicit even where the vocabulary is shared.

This is an implementation-facing consolidation document. It does not replace the specs.

## 1. Family Baseline Distribution Modes

The reference implementation starts with the simplest deterministic single-field distribution rules.

### `GRCV2`

- baseline `split_distribution_mode = "equal"`

### `GRCV3`

- baseline `split_distribution_mode = "equal"`

`GRCV3` may later support richer asymmetric strategies, but Phase 0 does not adopt them as the baseline.

### `GRC9`

- baseline `expansion_distribution_mode = "equal"`

### `GRC9V3`

- baseline `expansion_distribution_mode = "equal"`

These defaults are treated as implementation baselines, not as evidence that all families are semantically identical.

## 2. Curvature Backend Rollout

The allowed backend names come from the family specs, but the reference implementation rollout is fixed as:

1. baseline default: `curvature_backend = "none"`
2. first in-house backend to implement: `forman`
3. later advanced backend: `ollivier`

This ordering is intentional.

It preserves the Phase 0 backend boundary:

- no third-party graph library is required for the first executable models,
- the first authoritative curvature implementations belong to `PyGRC`,
- and advanced backends must not force the core model layer to depend on external graph packages.

## 3. Differential Reference Backend Commitment

The canonical implementation path for graph-intrinsic differential summaries is the reference backend defined in the `GRCV3` spec appendix.

Phase 0 therefore fixes the following commitment for the reference Python realization:

- `induced_local_frame` follows the spec-defined canonical backend first
- gradient summaries follow the same reference backend first
- Hessian summaries follow the same reference backend first

This means later phases should not invent a second default differential backend before the canonical one exists.

Alternative backends may be added later, but only as explicit alternatives with explicit serialization metadata.

## 4. Backend Policy

The authoritative execution backends are first-party and in-house.

That means:

- `src/pygrc/core/` and `src/pygrc/models/` must not depend on `networkx`, `pyvis`, or any other general-purpose graph/visualization library to execute model steps
- the first authoritative weighted-graph and port-graph implementations are owned by `PyGRC`
- backend pluggability is still a design goal, but it is achieved through protocols and adapters rather than through outsourcing the core execution substrate

### `networkx`

`networkx` is allowed only later as:

- adapter boundary
- interchange/import-export helper
- analysis helper outside the authoritative core execution path

It is not the reference execution substrate.

### `pyvis`

`pyvis` is allowed only later as:

- visualization/export tooling

It is not part of the simulation substrate.

## 5. Decision Recording Boundary

Phase 0 does **not** create a separate `DecisionLog.md`.

Instead:

- the checklist records the decision points,
- implementation notes record the rationale close to the affected work,
- and iteration summaries record the outcome.

For Phase 0, [`Phase-0-ImplementationChecklist.md`](./Phase-0-ImplementationChecklist.md) is therefore the authoritative execution and decision trail.

## 6. Consequences For Later Phases

These Phase 0 boundary decisions imply:

- `GRCV2` is the first executable baseline and uses the equal split default
- `GRC9` is implemented as a distinct port-graph substrate, not as a graph-family variant layered on top of `networkx`
- Phase 1 common contracts should expose the relevant modes and capability names without flattening family differences
- Phase 2 graph backends should be written for first-party determinism and stable IDs
- later adapter work belongs in integration-facing phases, not in the core bootstrap

## 7. Reference Links

The underlying normative sources are:

- [`specs/grc-common-interface.md`](../specs/grc-common-interface.md)
- [`specs/grc-v2-spec.md`](../specs/grc-v2-spec.md)
- [`specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)
- [`specs/grc-9-spec.md`](../specs/grc-9-spec.md)
- [`specs/grc-9-v3-spec.md`](../specs/grc-9-v3-spec.md)
