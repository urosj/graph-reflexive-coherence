"""Shared snapshot contract and canonical serialization helpers for PyGRC."""

from __future__ import annotations

from collections.abc import Mapping
import json
import math
import os
from pathlib import Path
import random
import tempfile
from types import MappingProxyType
from typing import Any, NotRequired, TypedDict

from .errors import SnapshotCompatibilityError
from .events import GRCEvent
from .ids import TOMBSTONE
from .storage import (
    PortEdgeRecord,
    PortGraphBackend,
    WeightedEdgeRecord,
    WeightedGraphBackend,
)
from .types import GRCState


SNAPSHOT_SCHEMA = "pygrc.snapshot"
SNAPSHOT_VERSION = 1
SNAPSHOT_GROUP_ORDER = (
    "metadata",
    "topology",
    "basin_attributes",
    "edge_labels",
    "dynamics",
    "observables",
    "events",
    "caches",
)


def canonicalize_json_value(value: Any) -> Any:
    """Convert supported values into deterministic JSON-safe data.

    The returned structure contains only JSON-native scalar, list, and mapping
    types, with deterministic ordering and rejection of unsupported or
    non-finite values.
    """

    if value is None or isinstance(value, bool | int | str):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("canonical JSON output does not allow non-finite floats")
        return value
    if isinstance(value, MappingProxyType):
        return {
            key: canonicalize_json_value(inner)
            for key, inner in sorted(value.items())
        }
    if isinstance(value, Mapping):
        non_string_keys = [key for key in value if not isinstance(key, str)]
        if non_string_keys:
            raise TypeError(
                "canonical JSON mappings require string keys; "
                f"got non-string keys {non_string_keys!r}"
            )
        return {
            key: canonicalize_json_value(inner)
            for key, inner in sorted(value.items())
        }
    if isinstance(value, list | tuple):
        return [canonicalize_json_value(item) for item in value]
    if isinstance(value, set | frozenset):
        canonical_items = [canonicalize_json_value(item) for item in value]
        return sorted(canonical_items, key=canonical_json_dumps)

    raise TypeError(
        "canonical JSON output does not support "
        f"values of type {type(value).__name__}"
    )


def canonical_json_dumps(data: Any) -> str:
    """Encode one value to the project's canonical JSON string form."""

    return json.dumps(
        canonicalize_json_value(data),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def _require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return value


def _require_int(value: Any, *, context: str) -> int:
    if not isinstance(value, int):
        raise SnapshotCompatibilityError(f"{context} must be an int")
    return value


def _require_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SnapshotCompatibilityError(f"{context} must be a float-compatible number")
    return float(value)


def _require_string_keyed_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    mapping = _require_mapping(value, context=context)
    non_string_keys = [key for key in mapping if not isinstance(key, str)]
    if non_string_keys:
        raise SnapshotCompatibilityError(
            f"{context} must use string keys; got non-string keys {non_string_keys!r}"
        )
    return mapping


class SnapshotMetadata(TypedDict, total=False):
    """Shared metadata group for all snapshot families."""

    snapshot_schema: str
    snapshot_version: int
    model_family: str
    model_version: NotRequired[str]
    file_format_version: NotRequired[int]
    step_index: int
    params: dict[str, Any]
    resolved_params: dict[str, Any]
    params_hash: str
    capabilities: list[str]
    rng_state: NotRequired[Any]
    next_node_id: NotRequired[int]
    next_edge_id: NotRequired[int]
    hessian_sign: NotRequired[Any]


class TopologySnapshot(TypedDict, total=False):
    """Shared topology group for snapshots."""

    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    incidence: NotRequired[dict[str, Any]]
    port_structure: NotRequired[dict[str, Any]]


class BaseSnapshot(TypedDict, total=False):
    """Shared top-level snapshot contract."""

    metadata: SnapshotMetadata
    topology: TopologySnapshot
    basin_attributes: NotRequired[dict[str, Any]]
    edge_labels: NotRequired[dict[str, Any]]
    dynamics: NotRequired[dict[str, Any]]
    observables: NotRequired[dict[str, Any]]
    events: NotRequired[list[dict[str, Any]]]
    caches: NotRequired[dict[str, Any]]


def _restore_python_random_state(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_restore_python_random_state(item) for item in value)
    return value


def serialize_rng_state(rng_state: Any) -> Any:
    """Serialize one RNG state through the shared persistence policy."""

    if rng_state is None:
        return None
    if isinstance(rng_state, Mapping) and isinstance(rng_state.get("engine"), str):
        return canonicalize_json_value(rng_state)
    if (
        isinstance(rng_state, tuple)
        and len(rng_state) == 3
        and isinstance(rng_state[0], int)
    ):
        return {
            "engine": "python_random",
            "state": canonicalize_json_value(rng_state),
        }
    return canonicalize_json_value(rng_state)


def deserialize_rng_state(payload: Any) -> Any:
    """Restore one RNG state from the shared serialized form."""

    if payload is None:
        return None
    if not isinstance(payload, Mapping):
        return canonicalize_json_value(payload)

    engine = payload.get("engine")
    if engine == "python_random":
        if "state" not in payload:
            raise SnapshotCompatibilityError(
                "python_random RNG payload must include state"
            )
        return _restore_python_random_state(payload["state"])
    return canonicalize_json_value(payload)


def serialize_runtime_rng_state(rng: random.Random | None) -> dict[str, Any] | None:
    """Serialize one runtime RNG object through the shared baseline format."""

    if rng is None:
        return None
    return serialize_rng_state(rng.getstate())


def build_state_payload(state: GRCState) -> dict[str, Any]:
    """Build one canonical JSON-safe payload from a shared model state."""

    return canonicalize_json_value(
        {
            "topology": state.topology,
            "node_values": state.node_values,
            "edge_values": state.edge_values,
            "step_index": state.step_index,
            "time": state.time,
            "budget_target": state.budget_target,
            "remainder": state.remainder,
            "cached_quantities": state.cached_quantities,
            "event_log": [
                {
                    "kind": event.kind,
                    "step_index": event.step_index,
                    "payload": event.payload,
                    "source_family": event.source_family,
                }
                for event in state.event_log
            ],
            "observables": state.observables,
            "rng_state": serialize_rng_state(state.rng_state),
            "params_identity": state.params_identity,
        }
    )


def restore_state_payload(payload: Mapping[str, Any]) -> GRCState:
    """Restore one shared model state from a serialized state payload."""

    mapping = _require_mapping(payload, context="state payload")
    event_log_payload = mapping.get("event_log", [])
    if not isinstance(event_log_payload, list):
        raise SnapshotCompatibilityError("state payload.event_log must be a list")

    event_log: list[GRCEvent] = []
    for index, event_payload in enumerate(event_log_payload):
        event_mapping = _require_mapping(
            event_payload, context=f"state payload.event_log[{index}]"
        )
        event_payload_mapping = _require_mapping(
            event_mapping.get("payload", {}),
            context=f"state payload.event_log[{index}].payload",
        )
        event_log.append(
            GRCEvent(
                kind=str(event_mapping.get("kind", "")),
                step_index=_require_int(
                    event_mapping.get("step_index"),
                    context=f"state payload.event_log[{index}].step_index",
                ),
                payload=dict(canonicalize_json_value(event_payload_mapping)),
                source_family=(
                    None
                    if event_mapping.get("source_family") is None
                    else str(event_mapping.get("source_family"))
                ),
            )
        )

    observables_payload = mapping.get("observables", {})
    if not isinstance(observables_payload, Mapping):
        raise SnapshotCompatibilityError("state payload.observables must be a mapping")
    cached_payload = mapping.get("cached_quantities", {})
    if not isinstance(cached_payload, Mapping):
        raise SnapshotCompatibilityError(
            "state payload.cached_quantities must be a mapping"
        )

    return GRCState(
        topology=canonicalize_json_value(mapping.get("topology")),
        node_values=canonicalize_json_value(mapping.get("node_values")),
        edge_values=canonicalize_json_value(mapping.get("edge_values")),
        step_index=_require_int(mapping.get("step_index", 0), context="state payload.step_index"),
        time=_require_float(mapping.get("time", 0.0), context="state payload.time"),
        budget_target=_require_float(
            mapping.get("budget_target", 0.0),
            context="state payload.budget_target",
        ),
        remainder=_require_float(
            mapping.get("remainder", 0.0), context="state payload.remainder"
        ),
        cached_quantities=dict(canonicalize_json_value(cached_payload)),
        event_log=event_log,
        observables=dict(canonicalize_json_value(observables_payload)),
        rng_state=deserialize_rng_state(mapping.get("rng_state")),
        params_identity=(
            None
            if mapping.get("params_identity") is None
            else str(mapping.get("params_identity"))
        ),
    )


def build_topology_snapshot(
    *,
    nodes: list[dict[str, Any]] | None = None,
    edges: list[dict[str, Any]] | None = None,
    incidence: Mapping[str, Any] | None = None,
    port_structure: Mapping[str, Any] | None = None,
) -> TopologySnapshot:
    """Build the shared topology group in canonical JSON-safe form."""

    topology: TopologySnapshot = {}
    if nodes is not None:
        topology["nodes"] = canonicalize_json_value(nodes)
    if edges is not None:
        topology["edges"] = canonicalize_json_value(edges)
    if incidence is not None:
        topology["incidence"] = canonicalize_json_value(incidence)
    if port_structure is not None:
        topology["port_structure"] = canonicalize_json_value(port_structure)
    return topology


def export_weighted_topology(graph: WeightedGraphBackend) -> TopologySnapshot:
    """Export one weighted backend into the shared deterministic topology group."""

    nodes = [
        {
            "node_id": node_id,
            "payload": canonicalize_json_value(graph.node_payload(node_id)),
        }
        for node_id in graph.iter_live_node_ids()
    ]
    edges = [
        {
            "edge_id": edge_id,
            "node_a": graph.edge_endpoints(edge_id)[0],
            "node_b": graph.edge_endpoints(edge_id)[1],
            "payload": canonicalize_json_value(graph.edge_payload(edge_id)),
        }
        for edge_id in graph.iter_live_edge_ids()
    ]
    incidence = {
        str(node_id): sorted(graph.incident_edge_ids(node_id))
        for node_id in graph.iter_live_node_ids()
    }
    return build_topology_snapshot(nodes=nodes, edges=edges, incidence=incidence)


def export_port_topology(graph: PortGraphBackend) -> TopologySnapshot:
    """Export one port backend into the shared deterministic topology group."""

    nodes = [
        {
            "node_id": node_id,
            "payload": canonicalize_json_value(graph.node_payload(node_id)),
        }
        for node_id in graph.iter_live_node_ids()
    ]
    edges = [
        {
            "edge_id": edge_id,
            "endpoint_a": {
                "node_id": graph.edge_ports(edge_id)[0][0],
                "slot": graph.edge_ports(edge_id)[0][1],
            },
            "endpoint_b": {
                "node_id": graph.edge_ports(edge_id)[1][0],
                "slot": graph.edge_ports(edge_id)[1][1],
            },
            "payload": canonicalize_json_value(graph.edge_payload(edge_id)),
        }
        for edge_id in graph.iter_live_edge_ids()
    ]
    incidence = {
        str(node_id): sorted(graph.incident_edge_ids(node_id))
        for node_id in graph.iter_live_node_ids()
    }
    port_structure = {
        str(node_id): {
            "ports": [
                {
                    "slot": slot,
                    "row": graph.port_slot_to_row_column(slot)[0],
                    "column": graph.port_slot_to_row_column(slot)[1],
                    "occupied": graph.port_is_occupied(node_id, slot),
                    "edge_id": graph.port_edge_id(node_id, slot),
                }
                for slot in graph.iter_port_slots(node_id)
            ]
        }
        for node_id in graph.iter_live_node_ids()
    }
    return build_topology_snapshot(
        nodes=nodes,
        edges=edges,
        incidence=incidence,
        port_structure=port_structure,
    )


def build_dynamics_group(*, state: Mapping[str, Any] | None = None, **sections: Any) -> dict[str, Any]:
    """Build one canonical JSON-safe dynamics group."""

    dynamics: dict[str, Any] = {}
    if state is not None:
        dynamics["state"] = canonicalize_json_value(state)
    for name, payload in sections.items():
        if payload is not None:
            dynamics[name] = canonicalize_json_value(payload)
    return dynamics


def build_event_records(events: list[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Build canonical JSON-safe event records for standard snapshots."""

    if events is None:
        return []
    canonical_events = canonicalize_json_value(events)
    if not isinstance(canonical_events, list):
        raise TypeError("canonical event records must normalize to a list")
    return canonical_events


def build_standard_snapshot(
    *,
    metadata: Mapping[str, Any],
    topology: Mapping[str, Any],
    basin_attributes: Mapping[str, Any] | None = None,
    edge_labels: Mapping[str, Any] | None = None,
    dynamics: Mapping[str, Any] | None = None,
    observables: Mapping[str, Any] | None = None,
    events: list[Mapping[str, Any]] | None = None,
    caches: Mapping[str, Any] | None = None,
    mutation_history: Any = None,
) -> BaseSnapshot:
    """Build one standard snapshot with canonical group ordering.

    Standard snapshots intentionally exclude mutation-history journals. Future
    exact-replay or machine-driver modes may add such data through separate
    extensions rather than by redefining the standard snapshot baseline.
    """

    if mutation_history is not None:
        raise ValueError(
            "standard snapshots do not include mutation-history journals"
        )

    canonical_groups: dict[str, Any] = {
        "metadata": canonicalize_json_value(metadata),
        "topology": canonicalize_json_value(topology),
        "basin_attributes": (
            None if basin_attributes is None else canonicalize_json_value(basin_attributes)
        ),
        "edge_labels": (
            None if edge_labels is None else canonicalize_json_value(edge_labels)
        ),
        "dynamics": None if dynamics is None else canonicalize_json_value(dynamics),
        "observables": (
            None if observables is None else canonicalize_json_value(observables)
        ),
        "events": None if events is None else build_event_records(events),
        "caches": None if caches is None else canonicalize_json_value(caches),
    }

    snapshot: BaseSnapshot = {}
    for group_name in SNAPSHOT_GROUP_ORDER:
        payload = canonical_groups[group_name]
        if payload is not None:
            snapshot[group_name] = payload
    return snapshot


def snapshot_to_json(snapshot: Mapping[str, Any]) -> str:
    """Encode one validated standard snapshot to canonical JSON text."""

    validate_snapshot_contract(snapshot)
    return canonical_json_dumps(snapshot)


def snapshot_from_json(payload: str | bytes) -> BaseSnapshot:
    """Decode one snapshot from JSON text or bytes using strict validation."""

    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SnapshotCompatibilityError(f"invalid snapshot JSON: {exc}") from exc
    if not isinstance(decoded, Mapping):
        raise SnapshotCompatibilityError("decoded snapshot must be a mapping")
    validate_snapshot_contract(decoded)
    return canonicalize_json_value(decoded)


def save_snapshot(path: str | Path, snapshot: Mapping[str, Any]) -> None:
    """Write one canonical snapshot atomically to disk."""

    target_path = Path(path)
    json_text = snapshot_to_json(snapshot)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=target_path.parent,
        prefix=f".{target_path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_file.write(json_text)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_path = Path(temp_file.name)
    os.replace(temp_path, target_path)


def load_snapshot(path: str | Path) -> BaseSnapshot:
    """Load one snapshot from disk using strict validation."""

    return snapshot_from_json(Path(path).read_text(encoding="utf-8"))


def restore_weighted_graph(topology: Mapping[str, Any], metadata: Mapping[str, Any]) -> WeightedGraphBackend:
    """Restore a weighted graph backend from validated snapshot groups."""

    node_records = topology.get("nodes", [])
    edge_records = topology.get("edges", [])
    if not isinstance(node_records, list):
        raise SnapshotCompatibilityError("topology.nodes must be a list")
    if not isinstance(edge_records, list):
        raise SnapshotCompatibilityError("topology.edges must be a list")

    next_node_id = (
        None
        if metadata.get("next_node_id") is None
        else _require_int(metadata.get("next_node_id"), context="metadata.next_node_id")
    )
    next_edge_id = (
        None
        if metadata.get("next_edge_id") is None
        else _require_int(metadata.get("next_edge_id"), context="metadata.next_edge_id")
    )
    node_slots: list[dict[str, Any] | Any] = []
    edge_slots: list[WeightedEdgeRecord | Any] = []

    for node_record in node_records:
        record = _require_mapping(node_record, context="weighted node record")
        node_id = _require_int(record.get("node_id"), context="weighted node record.node_id")
        payload = record.get("payload", {})
        node_payload = canonicalize_json_value(payload)
        while len(node_slots) < node_id:
            node_slots.append(TOMBSTONE)
        if len(node_slots) == node_id:
            node_slots.append(node_payload)
        else:
            raise SnapshotCompatibilityError("duplicate weighted node_id in topology")

    for edge_record in edge_records:
        record = _require_mapping(edge_record, context="weighted edge record")
        edge_id = _require_int(record.get("edge_id"), context="weighted edge record.edge_id")
        node_a = _require_int(record.get("node_a"), context="weighted edge record.node_a")
        node_b = _require_int(record.get("node_b"), context="weighted edge record.node_b")
        payload = canonicalize_json_value(record.get("payload", {}))
        while len(edge_slots) < edge_id:
            edge_slots.append(TOMBSTONE)
        if len(edge_slots) == edge_id:
            edge_slots.append(
                WeightedEdgeRecord(node_a=node_a, node_b=node_b, payload=payload)
            )
        else:
            raise SnapshotCompatibilityError("duplicate weighted edge_id in topology")

    return WeightedGraphBackend(
        node_slots=node_slots,
        edge_slots=edge_slots,
        next_node_id=next_node_id,
        next_edge_id=next_edge_id,
    )


def restore_port_graph(topology: Mapping[str, Any], metadata: Mapping[str, Any]) -> PortGraphBackend:
    """Restore a port graph backend from validated snapshot groups."""

    node_records = topology.get("nodes", [])
    edge_records = topology.get("edges", [])
    if not isinstance(node_records, list):
        raise SnapshotCompatibilityError("topology.nodes must be a list")
    if not isinstance(edge_records, list):
        raise SnapshotCompatibilityError("topology.edges must be a list")

    next_node_id = (
        None
        if metadata.get("next_node_id") is None
        else _require_int(metadata.get("next_node_id"), context="metadata.next_node_id")
    )
    next_edge_id = (
        None
        if metadata.get("next_edge_id") is None
        else _require_int(metadata.get("next_edge_id"), context="metadata.next_edge_id")
    )
    node_slots: list[dict[str, Any] | Any] = []
    edge_slots: list[PortEdgeRecord | Any] = []

    for node_record in node_records:
        record = _require_mapping(node_record, context="port node record")
        node_id = _require_int(record.get("node_id"), context="port node record.node_id")
        payload = canonicalize_json_value(record.get("payload", {}))
        while len(node_slots) < node_id:
            node_slots.append(TOMBSTONE)
        if len(node_slots) == node_id:
            node_slots.append(payload)
        else:
            raise SnapshotCompatibilityError("duplicate port node_id in topology")

    for edge_record in edge_records:
        record = _require_mapping(edge_record, context="port edge record")
        edge_id = _require_int(record.get("edge_id"), context="port edge record.edge_id")
        endpoint_a = _require_mapping(record.get("endpoint_a"), context="port edge record.endpoint_a")
        endpoint_b = _require_mapping(record.get("endpoint_b"), context="port edge record.endpoint_b")
        restored_record = PortEdgeRecord(
            endpoint_a=(
                _require_int(endpoint_a.get("node_id"), context="port edge endpoint_a.node_id"),
                _require_int(endpoint_a.get("slot"), context="port edge endpoint_a.slot"),
            ),
            endpoint_b=(
                _require_int(endpoint_b.get("node_id"), context="port edge endpoint_b.node_id"),
                _require_int(endpoint_b.get("slot"), context="port edge endpoint_b.slot"),
            ),
            payload=canonicalize_json_value(record.get("payload", {})),
        )
        while len(edge_slots) < edge_id:
            edge_slots.append(TOMBSTONE)
        if len(edge_slots) == edge_id:
            edge_slots.append(restored_record)
        else:
            raise SnapshotCompatibilityError("duplicate port edge_id in topology")

    return PortGraphBackend(
        node_slots=node_slots,
        edge_slots=edge_slots,
        next_node_id=next_node_id,
        next_edge_id=next_edge_id,
    )


def build_snapshot_metadata(
    *,
    model_family: str,
    step_index: int,
    params: dict[str, Any],
    resolved_params: dict[str, Any],
    params_hash: str,
    capabilities: set[str],
    model_version: str | None = None,
    file_format_version: int | None = None,
    rng_state: Any = None,
    next_node_id: int | None = None,
    next_edge_id: int | None = None,
    hessian_sign: Any = None,
) -> SnapshotMetadata:
    """Build the shared metadata group for a snapshot."""
    metadata: SnapshotMetadata = {
        "snapshot_schema": SNAPSHOT_SCHEMA,
        "snapshot_version": SNAPSHOT_VERSION,
        "model_family": model_family,
        "step_index": step_index,
        "params": params,
        "resolved_params": resolved_params,
        "params_hash": params_hash,
        "capabilities": sorted(capabilities),
    }
    if model_version is not None:
        metadata["model_version"] = model_version
    if file_format_version is not None:
        metadata["file_format_version"] = file_format_version
    if rng_state is not None:
        metadata["rng_state"] = serialize_rng_state(rng_state)
    if next_node_id is not None:
        metadata["next_node_id"] = next_node_id
    if next_edge_id is not None:
        metadata["next_edge_id"] = next_edge_id
    if hessian_sign is not None:
        metadata["hessian_sign"] = hessian_sign
    return metadata


def validate_snapshot_contract(snapshot: Mapping[str, Any]) -> None:
    """Validate that a snapshot satisfies the shared contract shape."""
    if "metadata" not in snapshot:
        raise SnapshotCompatibilityError("snapshot is missing metadata group")
    if "topology" not in snapshot:
        raise SnapshotCompatibilityError("snapshot is missing topology group")

    metadata = snapshot["metadata"]
    if not isinstance(metadata, Mapping):
        raise SnapshotCompatibilityError("metadata group must be a mapping")
    topology = snapshot["topology"]
    if not isinstance(topology, Mapping):
        raise SnapshotCompatibilityError("topology group must be a mapping")

    required_metadata = {
        "snapshot_schema",
        "snapshot_version",
        "model_family",
        "step_index",
        "params",
        "resolved_params",
        "params_hash",
        "capabilities",
    }
    missing_metadata = sorted(required_metadata - set(metadata))
    if missing_metadata:
        raise SnapshotCompatibilityError(
            f"metadata group is missing required fields: {missing_metadata}"
        )

    if metadata["snapshot_schema"] != SNAPSHOT_SCHEMA:
        raise SnapshotCompatibilityError(
            f"unsupported snapshot_schema: {metadata['snapshot_schema']!r}"
        )
    if metadata["snapshot_version"] != SNAPSHOT_VERSION:
        raise SnapshotCompatibilityError(
            f"unsupported snapshot_version: {metadata['snapshot_version']!r}"
        )
    if not isinstance(metadata["capabilities"], list):
        raise SnapshotCompatibilityError("metadata.capabilities must be a list")

    if "nodes" in topology and not isinstance(topology["nodes"], list):
        raise SnapshotCompatibilityError("topology.nodes must be a list when present")
    if "edges" in topology and not isinstance(topology["edges"], list):
        raise SnapshotCompatibilityError("topology.edges must be a list when present")


def require_snapshot_family(
    snapshot: Mapping[str, Any],
    *,
    expected_family: str,
) -> None:
    """Validate a snapshot and ensure that the model family matches."""
    validate_snapshot_contract(snapshot)
    metadata = snapshot["metadata"]
    if metadata["model_family"] != expected_family:
        raise SnapshotCompatibilityError(
            f"snapshot model_family {metadata['model_family']!r} does not match "
            f"expected family {expected_family!r}"
        )
