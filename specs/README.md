# GRC Library Specifications

This directory defines the specification for a Python library that implements
the synchronous Graph Reflexive Coherence model families and the first planned
Lorentzian/event-driven nine-port target.

1. `GRCV2`
2. `GRCV3`
3. `GRC9`
4. `GRC9V3`
5. `LGRC9V3`

The papers are the semantic source of truth. These specs translate that theory into a Python implementation contract.

The specification is split into two layers:

1. core model specifications for the best direct implementation of the papers,
2. integration specifications for downstream environments such as `ril_v0` and `ide_v0`.

The implementation strategy assumed by these specs is:

- core graph and port-graph backends are implemented in-house,
- core models depend on backend protocols rather than third-party graph libraries,
- and external tools such as `networkx` or `pyvis` may be added later only as adapters, interchange helpers, or visualization layers.

## Documents

- `grc-common-interface.md`
  Common abstract model interface, shared datatypes, lifecycle, events, diagnostics, and capability model.
- `grc-v2-spec.md`
  Baseline graph Reflexive Coherence implementation from `papers/2025-12-GRC-V2.md`, with single dynamical conductance and shared analytic edge labels.
- `grc-v3-spec.md`
  Basin-attribute and multi-metric implementation from `papers/2026-02-GRC-V3.md`.
- `grc-9-spec.md`
  Nine-slot mechanical substrate implementation from `papers/2026-04-GRC-9.md`, with single dynamical conductance and shared analytic edge labels.
- `grc-9-v3-spec.md`
  Hybrid implementation: G‑RC‑9 substrate with GRC‑v3 semantic lift, especially basin attributes, signed-Hessian hybrid spark semantics, and explicit separation between default Lane A and the opt-in `grc9v3_column_h_assisted` spark lane.
- `lgrc-9-v3-spec.md`
  Lorentzian/event-driven nine-port V3 target. The file uses the hyphenated
  paper/spec naming convention, while the executable runtime name is
  `LGRC9V3`. The first implementation level is LGRC-0 annotation/timing
  evidence over `GRC9V3`; behavior-changing LGRC-1 is opt-in and semi-causal
  unless causal availability buffers exist.
- `lgrc-9-v3-restoration-identity.md`
  Implemented and validated versioned LGRC9V3 restoration-identity contract
  over LGRC runtime state and a read-only projection of its embedded GRC9V3
  state. V1 identifies current state; v2 additionally identifies the persisted
  reset baseline. Both remain distinct from raw snapshot identity.
- `grc-reset-baseline-persistence.md`
  Repository-wide save/load/reset lifecycle contract for all concrete model
  families. It adds a versioned reset-baseline snapshot group without changing
  the shared snapshot schema version or runtime dynamics.
- `grc-integration-layer.md`
  Adapter-layer contract for exposing core models to downstream runtimes without constraining core model design.
- `grc-machine-driver.md`
  Machine-driver contract for IDE-style inspection, snapshotting, patching, and deterministic tooling workflows.
- `grc-embedding-profile.md`
  Lightweight embedding profile for external projects that want to adopt a GRC-backed graph and `step()` loop first, with optional later IDE attachment.

## Family Capability Matrix

| Family | Dynamic transport | Analytic edge labels | Frame baseline | Boundary baseline | Semantic depth |
| --- | --- | --- | --- | --- | --- |
| `GRCV2` | single scalar conductance | shared three-label family, selectable | graph-derived or host-supplied, explicit by `frame_mode` | `prune` by default, richer modes optional | minimal graph realization |
| `GRCV3` | single scalar base conductance | shared three-label family, selectable | graph-derived or host-supplied, explicit by `frame_mode` | explicit `boundary_mode` | basin-attribute / hierarchy semantics |
| `GRC9` | single scalar conductance per occupied port-pair | shared three-label family, selectable | fixed intrinsic nine-slot chart | no dedicated pass required; optional `boundary_mode` | mechanical substrate semantics |
| `GRC9V3` | single scalar base conductance per occupied port-pair | shared three-label family, selectable | fixed intrinsic nine-slot chart | explicit `boundary_mode` | combined mechanical + semantic lift |
| `LGRC9V3` | inherited `GRC9V3` transport in LGRC-0; future causal transport only with explicit accounting | inherited labels plus causal delay policy | fixed intrinsic nine-slot chart plus causal-history timing fields | inherited `GRC9V3` boundary in LGRC-0 | causal-history annotation / semi-causal fixed-topology eligibility |

Across the whole family matrix, the broader extension capabilities are shared vocabulary rather than `v3`-only concepts:

- `boundary_barrier`
- `causal_layer`
- `anisotropic_edges`
- `multiscale_sigma`

Not every family must implement them by default, and they should not be used to erase family boundaries. The point of the shared vocabulary is:

- every family can state clearly which of these extensions it may support,
- every family can state clearly which it must not claim,
- and any family that does implement one must expose it under the same name and serialize the constitutive choices that make it meaningful.

## Intended Package Shape

The specs assume a package shaped roughly like:

```text
pygrc/
  __init__.py
  core/
    interfaces.py
    types.py
    events.py
    graph.py
    observables.py
  models/
    grc_v2.py
    grc_v3.py
    grc_9.py
    grc_9_v3.py
    lgrc_9_v3.py
  integrations/
    ril_v0/
    ide_v0/
  utils/
    curvature.py
    shortest_paths.py
    simplex.py
    serialization.py
```

This layout is guidance, not a hard requirement. The hard requirements are:

- all implemented model families expose the common interface specified in
  `grc-common-interface.md`,
- the core package remains independent of downstream integrations,
- and integration adapters depend on core models rather than the reverse.
