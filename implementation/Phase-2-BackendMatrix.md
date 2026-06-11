# Phase 2 Backend Matrix

This document records the backend and adapter attachment story established
during **Phase 2: Core Graph + Storage**.

It is a companion to:

- [`Phase-2-ImplementationPlan.md`](./Phase-2-ImplementationPlan.md)
- [`Phase-2-ImplementationChecklist.md`](./Phase-2-ImplementationChecklist.md)

The point of this matrix is to make one boundary explicit:

- the authoritative execution substrate remains in-house,
- optional third-party adapters attach later through the integration layer,
- and those adapters target the protocol surface established in `src/pygrc/core/`.

## Core Rule

The following are authoritative for execution:

- `WeightedGraphBackend` for `GRCV2` / `GRCV3`
- `PortGraphBackend` for `GRC9` / `GRC9V3`

The following are **not** authoritative for execution:

- `networkx`
- `pyvis`
- any future general-purpose graph or visualization package

## Attachment Matrix

| Family Group | Authoritative Backend | Protocol Target | Future Adapter Role | Integration Boundary |
| --- | --- | --- | --- | --- |
| `GRCV2` / `GRCV3` | `WeightedGraphBackend` | `WeightedGraphProtocol` | interchange, analysis, import/export | `src/pygrc/integrations/graph_adapter_boundary.py` |
| `GRC9` / `GRC9V3` | `PortGraphBackend` | `PortGraphProtocol` | interchange, analysis, import/export | `src/pygrc/integrations/graph_adapter_boundary.py` |
| weighted or projected views | authoritative backend remains in-house | protocol layer or exported snapshot/view | visualization/export only | `src/pygrc/integrations/graph_adapter_boundary.py` |

## Future `networkx` Boundary

If a future `networkx` adapter is added:

- it belongs in `src/pygrc/integrations/`
- it may depend on `networkx`
- it may export from the authoritative in-house backends
- it may import into the authoritative in-house backends
- it must not become the execution substrate for model stepping

The intended attachment point is:

- `WeightedGraphProtocol` for ordinary graph families
- `PortGraphProtocol` for nine-slot families

This means a future adapter should depend on protocol-observable behavior such as:

- live deterministic iteration
- stable IDs
- adjacency/incidence lookup
- port occupancy and rewiring visibility where relevant

It should not depend on:

- `TombstoneSlotTable` internals
- adjacency-map internals
- raw storage list layout

## Future `pyvis` Boundary

If a future `pyvis` adapter is added:

- it belongs in `src/pygrc/integrations/`
- it is visualization/export only
- it should consume a read-only graph view, exported records, or snapshots
- it must not be required to execute core graph/storage operations

The intended attachment point is read-only export from:

- `WeightedGraphProtocol`
- `PortGraphProtocol`
- or later snapshot/export helpers built on top of them

## Design Consequences

The Phase 2 protocol surface must therefore stay:

- behavioral rather than storage-shaped
- deterministic in ordering
- explicit about stable IDs
- explicit about port occupancy and slot conversion
- independent of third-party graph libraries

If a future adapter cannot satisfy the integration-side boundary without
requiring changes to core model code, that means the adapter boundary was
drawn incorrectly.
