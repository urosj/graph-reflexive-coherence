# Phase 0 Determinism Conventions

This document records the deterministic implementation conventions chosen during **Phase 0**.

It is implementation-facing guidance for later phases, especially:

- Phase 1 common contracts,
- Phase 2 graph/storage backends,
- Phase 3 serialization and snapshot support.

These conventions are intended to remove ambiguity before model/state code exists.

## Scope

This document fixes the reference implementation defaults for:

- ID type and format,
- deterministic ordering,
- event-log ordering,
- canonical snapshot grouping,
- float comparison categories,
- snapshot naming/versioning,
- tombstone and ID-reuse behavior.

These are implementation conventions for the reference Python realization. They do not change the public specs, but they are expected to be followed unless later decisions explicitly revise them.

## 1. Canonical ID Types

The reference implementation uses **stable integer IDs**.

### Node IDs

- Type: `int`
- Domain: non-negative
- Allocation rule: monotone increasing
- First allocated node ID: `0`

### Edge IDs

- Type: `int`
- Domain: non-negative
- Allocation rule: monotone increasing
- First allocated edge ID: `0`

### Port Identifiers

For `GRC9` and `GRC9V3`, the canonical internal port identifier is a single integer slot ID.

- Type: `int`
- Domain: `0..8`
- Allocation rule: fixed, not dynamic

Canonical row/column conversion uses **zero-based row-major order**:

```text
slot_id = 3 * row + col
row = slot_id // 3
col = slot_id % 3
```

with:

- `row in {0, 1, 2}`
- `col in {0, 1, 2}`

This means the canonical slot order is:

```text
0 1 2
3 4 5
6 7 8
```

Human-facing labels may be added later, but they are derived labels only. They are not canonical storage identities.

## 2. Stable ID Policy

IDs are **never reused** within a model instance.

The reference implementation assumes:

- node creation increments `next_node_id`,
- edge creation increments `next_edge_id`,
- deletions do not recycle identifiers,
- and replay/save-load behavior preserves these counters.

This avoids identity drift after prune, split, birth, or expansion events.

## 3. Tombstone Policy

The default storage expectation is **tombstoned slots rather than ID reuse**.

That means:

- internal node/edge arrays may retain removed slots,
- dead slots remain addressable internally by their former IDs,
- live iteration must skip tombstoned entries,
- and new objects always allocate fresh IDs.

For canonical snapshots:

- live records are serialized,
- `next_node_id` and `next_edge_id` are serialized,
- tombstoned slots are not required to appear as empty records in the canonical snapshot,
- but later machine-driver or exact-replay tooling may add explicit tombstone metadata if needed.

## 4. Deterministic Ordering Rules

### Node Order

- Canonical node order is ascending `node_id`.

### Edge Order

- Canonical edge order is ascending `edge_id`.

### Neighbor Order

When a node-local operation needs a deterministic neighbour scan, the canonical order is:

1. ascending neighbour `node_id`
2. then ascending incident `edge_id`

This rule applies even if the backend stores adjacency differently.

### Port Order

For `GRC9` and `GRC9V3`, canonical port order is ascending `slot_id` (`0..8`).

### Port-Pair / Occupied Edge Order

Occupied port-pair records are ordered by ascending `edge_id`.

If a node-local port view is needed, ports are scanned in ascending `slot_id`.

## 5. Event Log Ordering

The event log is ordered by **deterministic emission order**, not by wall-clock time.

The canonical rule is:

1. event groups follow the step pipeline order of the model family,
2. within each pipeline phase, live entities are scanned in ascending stable ID order,
3. emitted events are appended in encounter order,
4. if an implementation batches events temporarily, it must restore the same deterministic order before exposing or serializing them.

This avoids requiring a global event-rank table while still producing a stable log.

## 6. Canonical Snapshot Group Order

The canonical top-level snapshot group order is:

1. `metadata`
2. `topology`
3. `basin_attributes`
4. `edge_labels`
5. `dynamics`
6. `observables`
7. `events`
8. `caches`

If a group is unsupported by a family, it may be omitted, but the relative order of the remaining groups must be preserved.

### Metadata Group

`metadata` should contain values such as:

- `snapshot_schema`
- `snapshot_version`
- `model_family`
- `model_version` if present
- `step_index`
- `params`
- `resolved_params`
- `params_hash`
- `capabilities`
- `rng_state` if stored
- `next_node_id`
- `next_edge_id`
- `hessian_sign` for `GRCV3` / `GRC9V3` when signed-Hessian semantics are enabled or canonicalized

### Topology Group

`topology` should contain:

- node records
- edge records
- connectivity or incidence data
- port occupancy / port-edge structure for `GRC9` families

Canonical node and edge tables are serialized as **lists of records**, not arbitrary ID-keyed mappings.

This avoids ambiguity caused by stringified integer keys and makes ordering explicit.

### Basin Attributes Group

`basin_attributes` is the canonical home for spec-defined basin bundles such as:

- coherence
- gradient summaries
- Hessian summaries
- net flux summaries
- effective basin mass
- basin IDs / parent IDs / depth where relevant

Families that do not expose basin attributes omit this group.

### Edge Labels Group

`edge_labels` is the canonical home for:

- `base_conductance`
- `geometric_length`
- `temporal_delay`
- `flux_coupling`
- `edge_label_selection`
- `edge_label_computation_mode`
- `edge_label_params`

### Dynamics Group

`dynamics` is the canonical home for evolving state such as:

- fluxes
- potentials
- split or expansion progress
- choice/collapse state if present
- budget remainder / measure bookkeeping

### Observables / Events / Caches

- `observables` contains computed summary observables,
- `events` contains the deterministic event log,
- `caches` contains optional derived caches that are intentionally serialized.

## 7. Float And Equality Policy

The reference implementation uses two comparison categories.

### Exact Equality Required

Exact equality is required for:

- IDs
- counts
- booleans
- mode strings
- capability names
- event ordering
- topology incidence structure
- port occupancy structure
- canonical hashes
- snapshot group order

### Numeric Tolerance Allowed

Tolerance-based comparison is allowed for floating-point quantities such as:

- coherence
- conductance
- geometric labels
- fluxes
- potentials
- gradients
- Hessians
- observables derived from floating state

Default verification tolerances:

- `abs_tol = 1e-12`
- `rel_tol = 1e-9`

Budget-specific acceptance may use a stricter rule when the family claims exact preservation with an explicit remainder channel. In that case the canonical check is against the represented remainder, not against ad hoc drift.

Non-finite floats are not allowed in canonical snapshots.

## 8. Snapshot Naming And Versioning

The canonical snapshot schema label for the reference implementation starts at:

- `snapshot_schema = "pygrc.snapshot"`
- `snapshot_version = 1`

If snapshots are written to disk, the canonical file naming pattern is:

```text
{model_family_lower}-step-{step_index:08d}.json
```

Examples:

```text
grcv2-step-00000000.json
grcv3-step-00000125.json
grc9-step-00000042.json
grc9v3-step-00001024.json
```

Timestamps are not part of canonical snapshot names.

## 9. JSON And Serialization Safety

Canonical JSON snapshots should:

- be UTF-8 text,
- use LF line endings,
- avoid NaN/Inf values,
- preserve the canonical top-level group order,
- serialize ordered tables as lists in canonical order.

The goal is deterministic replay and comparison, not merely valid JSON.

## 10. Consequences For Later Phases

These conventions imply the following defaults for later implementation work:

- graph/storage backends should be array-friendly and ID-stable,
- deletion paths should assume tombstoning rather than ID recycling,
- snapshot builders should produce grouped ordered structures,
- and tests should compare discrete structure exactly while using documented tolerances for floating state.
