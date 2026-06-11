# GRC Machine Driver Specification

## Purpose

This document specifies a machine-driver layer for exposing GRC model instances to debugger-style and IDE-style environments.

The driver is an integration concern. It is not part of the core `GRCModel` contract.

Its role is to present:

- deterministic inspection,
- stable serialization,
- snapshot and patch workflows,
- budget and invariant checks,
- edit planning and application,
- and compact telemetry views.

## Relationship To Core Models

The machine driver wraps one concrete model family implementation.

It may wrap:

- `GRCV2`,
- `GRCV3`,
- `GRC9`,
- `GRC9V3`.

The driver must not redefine model behavior. It may only:

- inspect,
- serialize,
- snapshot,
- replay,
- or apply explicit edits against the underlying model/state.

## Driver Identity

Each machine driver must expose an identity triple:

```python
@dataclass(frozen=True)
class DriverIdentity:
    family: str
    version: str
    impl: str
```

Typical values:

- `family="GRC"`
- `version="v0"`
- `impl="pygrc.ide_v0"`

## Required Responsibilities

### Inspection

The driver must provide deterministic read-only views over the machine state.

Minimum inspection surfaces:

- state summary,
- node inspection,
- edge inspection,
- basin inspection,
- budget inspection,
- local observer view,
- spark report,
- invariant report.

### Deterministic serialization

The driver must serialize state deterministically.

The same logical state must produce identical bytes and identical digest values across repeated serializations within the same implementation version.

### Snapshot and patch support

The driver must support:

- serializing whole state snapshots,
- diffing two states into a reversible patch format,
- applying a patch,
- rolling back a patch,
- computing stable digests for both states and patches.

The patch format is implementation-defined, but it must be deterministic and reversible.

### Freeze/thaw

The driver should support immutable snapshotting for debugger checkpointing:

```python
def freeze_state(self, state) -> Any: ...
def thaw_state(self, frozen) -> OpaqueState: ...
```

This allows fast checkpoint/replay without forcing the debugger to know the internal model structure.

## Driver Surface

The recommended surface matches existing IDE expectations closely:

```python
class GRCMachineDriver(Protocol):
    identity: DriverIdentity

    def state_summary(self, state) -> dict: ...
    def get_node(self, state, node_id: str) -> dict: ...
    def list_nodes(self, state, selector: dict | None = None) -> list[dict]: ...
    def basin_report(self, state) -> dict: ...
    def spark_report(self, state) -> dict: ...
    def observer_view(self, state, origin: str, policy: dict) -> dict: ...

    def schema(self, state) -> dict: ...
    def inspect_node(self, state, node_id: str, fields: list[str] | None = None) -> dict: ...
    def inspect_edge(self, state, u: str, v: str, fields: list[str] | None = None) -> dict: ...
    def inspect_basin(self, state, sink_id: str, fields: list[str] | None = None, members_mode: str = "count", top_k: int | None = None) -> dict: ...
    def inspect_budget(self, state) -> dict: ...
    def telemetry_snapshot(self, state) -> dict: ...

    def invariants_check(self, state) -> dict: ...
    def budget_project(self, state) -> dict: ...

    def plan_edit_group(self, state, ops: list[dict], budget_policy: dict) -> dict: ...
    def apply_edit_group(self, state, ops: list[dict], budget_policy: dict): ...

    def diff_states(self, before, after) -> bytes: ...
    def apply_patch(self, state, patch: bytes): ...
    def rollback_patch(self, state, patch: bytes): ...
    def patch_digest(self, patch: bytes) -> str: ...

    def state_serialize(self, state) -> bytes: ...
    def state_deserialize(self, blob: bytes): ...
    def state_digest(self, state) -> str: ...

    def freeze_state(self, state) -> Any: ...
    def thaw_state(self, frozen: Any): ...
```

This is the driver contract, not the core model contract.

## State Summary Contract

`state_summary()` should return a compact summary suitable for command-line or IDE display.

Minimum fields:

- `model_family`
- `step_index`
- `time`
- `num_nodes`
- `num_edges`
- `budget_current`
- `budget_target`
- `budget_error`
- `capabilities`

Recommended optional fields:

- `num_identities`
- `num_soft_splits`
- `num_sparks_last`
- `abundance`
- `weighted_abundance`
- `visibility_modes`

## Inspection Semantics

### Node inspection

Node inspection must use stable node identifiers as strings at the driver boundary.

Returned data may include:

- coherence,
- potential,
- identity assignment,
- basin attributes,
- row/column data for `GRC9`,
- hierarchy or lineage fields for `GRCV3` / `GRC9V3`.

### Edge inspection

Edge inspection must identify edges deterministically by endpoints or by a stable edge ID when available.

Returned data may include:

- weight or base conductance,
- flux,
- curvature proxies,
- distance labels,
- port labels,
- v3 analytic labels.

### Basin inspection

Basin inspection must distinguish:

- sink representative,
- basin members or member count,
- basin mass,
- spark-related diagnostics,
- v3 basin attributes when present.

### Local observer view

The driver must support a deterministic restricted-view projection for tools that need observer-local inspection rather than full-state inspection.

Minimum policy keys:

- `radius`
- `include_edges`
- `include_boundary`
- `field_mask`

Minimum returned fields:

- `origin`
- `visible_nodes`
- `visible_edges`
- `boundary_nodes`
- `withheld_fields`
- `policy`

This facility is an inspection boundary only. It must not silently redefine the underlying model dynamics.

## Edit Groups

Edit groups are integration-level explicit state modifications used by assemblers, debug tooling, or scripted mutation workflows.

The driver may support operations such as:

- add/remove node,
- add/remove edge,
- set node coherence,
- set edge weight,
- assign port,
- force split progress,
- attach metadata.

Edit-group planning must:

- validate operation schemas,
- determine touched entities,
- state budget implications,
- reject unsupported edits for the current model family.

Edit-group application must either:

- apply the whole group,
- or fail without partial mutation.

## Invariants

`invariants_check()` must never raise for expected validation failures. It should return structured results.

Minimum invariant domains:

- graph consistency,
- field alignment,
- budget consistency,
- non-negative coherence after correction,
- family-specific topology invariants.

## Determinism Requirements

The driver must define deterministic ordering for:

- node lists,
- edge lists,
- basin member lists when returned,
- snapshot serialization,
- patch encoding,
- digest computation.

If a feature depends on randomness, the driver must capture and serialize enough RNG state to preserve replay.

Visibility-restricted queries must also be deterministic: the same state and policy must produce the same visible subgraph ordering and the same withheld-field markers.

## Family-Specific Extensions

The driver may expose additional fields by family:

- `GRCV2`: sink-based identities, soft splits, mass remainder, conductance sparks.
- `GRCV3`: basin attributes, hierarchy, choice/collapse registries, analytic edge labels.
- `GRC9`: ordered ports, row/column occupancy, mechanical spark state, refinement status.
- `GRC9V3`: both nine-port structure and v3 semantic overlays.

The driver must not pretend all families support the same depth of inspection.

## Error Model

Machine-driver methods should return structured errors at the integration boundary rather than raising raw internal exceptions for expected invalid requests.

Typical error classes:

- invalid entity reference,
- unsupported field,
- unsupported capability,
- invalid patch,
- serialization failure,
- invariant violation,
- invalid edit group.

## Guidance For Reference Implementation

The reference implementation should build machine drivers as wrappers over core models and model snapshots rather than embedding IDE-specific logic inside the model classes.

A reasonable layout is:

```text
pygrc/integrations/ide_v0/
  machine_driver.py
  serializers.py
  patches.py
  telemetry.py
  inspect.py
```

This preserves the independence of the paper-driven core layer while making debugger and runtime tooling practical.
