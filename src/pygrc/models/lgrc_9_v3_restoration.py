"""Restoration-identity projections owned by the LGRC9V3 runtime."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import math
from typing import Any

from pygrc.core import (
    GRCModel,
    SnapshotCompatibilityError,
    canonicalize_json_value,
    digest_canonical_data,
    require_snapshot_family,
)

from .grc_9_v3 import GRC9V3
from .lgrc_9_v3_runtime_state import restore_lgrc9v3_runtime_state_artifact


LGRC9V3_EMBEDDED_GRC9V3_STATE_KIND = "lgrc9v3_embedded_grc9v3_state"
LGRC9V3_EMBEDDED_GRC9V3_STATE_SCHEMA_VERSION = "lgrc9v3_embedded_grc9v3_state_v1"
LGRC9V3_RESTORATION_IDENTITY_KIND = "lgrc9v3_restoration_identity"
LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION = "lgrc9v3_restoration_identity_v1"

_INCLUDED_STATE_GROUPS = (
    "resolved_parameter_identity",
    "topology_and_stable_allocation",
    "node_basin_hierarchy_and_expansion_state",
    "canonical_port_edges_and_analytic_edge_labels",
    "potential_sink_set_and_basin_membership",
    "choice_collapse_and_coarse_state",
    "step_time_budget_and_remainder",
    "rng_event_observable_and_cached_state",
    "normalized_base_events_and_observables",
)

_EXCLUDED_REPRESENTATION_FIELDS = (
    "raw_full_snapshot_digest",
    "mapping_insertion_order",
    "undirected_topology_endpoint_order",
    "undirected_port_edge_endpoint_order_after_signed_flux_canonicalization",
    "signed_zero_of_zero_port_edge_flux",
    "absence_before_deterministic_default_materialization",
    "duplicate_outer_grc9v3_snapshot_groups",
)

_COMPOSITE_INCLUDED_STATE_GROUPS = (
    "embedded_grc9v3_state",
    "exact_lgrc9v3_runtime_artifact",
    "lgrc9v3_events",
    "lgrc9v3_observables",
    "source_snapshot_schema_and_version",
)

_COMPOSITE_EXCLUDED_REPRESENTATION_FIELDS = (
    "raw_full_snapshot_digest",
    "raw_snapshot_file_bytes",
    "duplicate_outer_topology_basin_and_edge_groups",
    "raw_embedded_grc9v3_snapshot_representation",
)


def _require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotCompatibilityError(f"{context} must be a mapping")
    return value


def _require_int(value: Any, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SnapshotCompatibilityError(f"{context} must be an int")
    return value


def _require_number(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SnapshotCompatibilityError(f"{context} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise SnapshotCompatibilityError(f"{context} must be finite")
    return number


def _endpoint_key(endpoint: Mapping[str, Any], *, context: str) -> tuple[int, int]:
    try:
        node_id = endpoint["node_id"]
        slot = endpoint["slot"]
    except KeyError as exc:
        raise SnapshotCompatibilityError(
            f"{context} must include node_id and slot"
        ) from exc
    return (
        _require_int(node_id, context=f"{context}.node_id"),
        _require_int(slot, context=f"{context}.slot"),
    )


def _canonical_topology(topology: Mapping[str, Any]) -> dict[str, Any]:
    canonical = dict(deepcopy(topology))
    edges = canonical.get("edges", [])
    if not isinstance(edges, list):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 topology.edges must be a list"
        )

    canonical_edges: list[dict[str, Any]] = []
    for index, raw_edge in enumerate(edges):
        context = f"embedded GRC9V3 topology.edges[{index}]"
        edge = dict(
            _require_mapping(
                raw_edge,
                context=context,
            )
        )
        edge_id = _require_int(edge.get("edge_id"), context=f"{context}.edge_id")
        endpoint_a = _require_mapping(
            edge.get("endpoint_a"),
            context=f"{context}.endpoint_a",
        )
        endpoint_b = _require_mapping(
            edge.get("endpoint_b"),
            context=f"{context}.endpoint_b",
        )
        if _endpoint_key(endpoint_b, context="endpoint_b") < _endpoint_key(
            endpoint_a,
            context="endpoint_a",
        ):
            endpoint_a, endpoint_b = endpoint_b, endpoint_a
        edge["endpoint_a"] = dict(endpoint_a)
        edge["endpoint_b"] = dict(endpoint_b)
        edge["edge_id"] = edge_id
        canonical_edges.append(edge)
    canonical["edges"] = sorted(
        canonical_edges,
        key=lambda edge: edge["edge_id"],
    )
    return dict(canonicalize_json_value(canonical))


def _port_endpoint_key(
    edge: Mapping[str, Any],
    *,
    node_key: str,
    port_key: str,
    context: str,
) -> tuple[int, int]:
    node_id = edge.get(node_key)
    port_id = edge.get(port_key)
    return (
        _require_int(node_id, context=f"{context}.{node_key}"),
        _require_int(port_id, context=f"{context}.{port_key}"),
    )


def _canonical_port_edges(value: Any) -> dict[str, Any]:
    edges = _require_mapping(value, context="embedded GRC9V3 state.port_edges")
    canonical: dict[str, Any] = {}
    for edge_id, raw_edge in edges.items():
        if not isinstance(edge_id, str):
            raise SnapshotCompatibilityError(
                "embedded GRC9V3 state.port_edges must use string keys"
            )
        context = f"embedded GRC9V3 state.port_edges[{edge_id!r}]"
        edge = dict(_require_mapping(raw_edge, context=context))
        endpoint_u = _port_endpoint_key(
            edge,
            node_key="node_u",
            port_key="port_u",
            context=context,
        )
        endpoint_v = _port_endpoint_key(
            edge,
            node_key="node_v",
            port_key="port_v",
            context=context,
        )
        edge["conductance"] = _require_number(
            edge.get("conductance"),
            context=f"{context}.conductance",
        )
        canonical_flux = _require_number(
            edge.get("flux_uv"),
            context=f"{context}.flux_uv",
        )
        if endpoint_v < endpoint_u:
            endpoint_u, endpoint_v = endpoint_v, endpoint_u
            canonical_flux = -canonical_flux
        if canonical_flux == 0.0:
            canonical_flux = 0.0
        edge.update(
            {
                "node_u": endpoint_u[0],
                "port_u": endpoint_u[1],
                "node_v": endpoint_v[0],
                "port_v": endpoint_v[1],
                "flux_uv": canonical_flux,
            }
        )
        canonical[edge_id] = edge
    return dict(canonicalize_json_value(canonical))


def _stable_allocation(
    metadata: Mapping[str, Any],
    topology: Mapping[str, Any],
) -> dict[str, Any]:
    next_node_id = _require_int(
        metadata.get("next_node_id"),
        context="normalized embedded GRC9V3 metadata.next_node_id",
    )
    next_edge_id = _require_int(
        metadata.get("next_edge_id"),
        context="normalized embedded GRC9V3 metadata.next_edge_id",
    )
    nodes = topology.get("nodes", [])
    edges = topology.get("edges", [])
    if not isinstance(nodes, list):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 topology.nodes must be a list"
        )
    if not isinstance(edges, list):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 topology.edges must be a list"
        )
    live_node_ids = sorted(
        _require_int(
            _require_mapping(record, context="embedded GRC9V3 topology node").get(
                "node_id"
            ),
            context="embedded GRC9V3 topology node.node_id",
        )
        for record in nodes
    )
    live_edge_ids = sorted(
        _require_int(
            _require_mapping(record, context="embedded GRC9V3 topology edge").get(
                "edge_id"
            ),
            context="embedded GRC9V3 topology edge.edge_id",
        )
        for record in edges
    )
    if len(set(live_node_ids)) != len(live_node_ids):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 topology node IDs must be unique"
        )
    if len(set(live_edge_ids)) != len(live_edge_ids):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 topology edge IDs must be unique"
        )
    if any(node_id < 0 or node_id >= next_node_id for node_id in live_node_ids):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 live node IDs must be below next_node_id"
        )
    if any(edge_id < 0 or edge_id >= next_edge_id for edge_id in live_edge_ids):
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 live edge IDs must be below next_edge_id"
        )
    live_nodes = set(live_node_ids)
    live_edges = set(live_edge_ids)
    return {
        "next_node_id": next_node_id,
        "next_edge_id": next_edge_id,
        "live_node_ids": live_node_ids,
        "live_edge_ids": live_edge_ids,
        "node_slot_status": [
            "live" if node_id in live_nodes else "tombstone"
            for node_id in range(next_node_id)
        ],
        "edge_slot_status": [
            "live" if edge_id in live_edges else "tombstone"
            for edge_id in range(next_edge_id)
        ],
    }


def build_lgrc9v3_embedded_grc9v3_state_v1(
    snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the internal canonical base-state component for one LGRC9V3 snapshot.

    The input is deep-copied before the current GRC9V3 loader materializes its
    deterministic defaults. No source model, snapshot, or GRC9V3 behavior is
    changed by this projection.
    """

    if not isinstance(snapshot, Mapping):
        raise SnapshotCompatibilityError("LGRC9V3 restoration source must be a mapping")
    require_snapshot_family(snapshot, expected_family="LGRC9V3")

    try:
        normalized_model = _normalized_embedded_grc9v3_model(snapshot)
        normalized_snapshot = normalized_model.snapshot()
    except SnapshotCompatibilityError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 snapshot could not be normalized"
        ) from exc

    metadata = _require_mapping(
        normalized_snapshot.get("metadata"),
        context="normalized embedded GRC9V3 metadata",
    )
    topology = _require_mapping(
        normalized_snapshot.get("topology"),
        context="normalized embedded GRC9V3 topology",
    )
    dynamics = _require_mapping(
        normalized_snapshot.get("dynamics"),
        context="normalized embedded GRC9V3 dynamics",
    )
    state = dict(
        _require_mapping(
            dynamics.get("state"),
            context="normalized embedded GRC9V3 dynamics.state",
        )
    )
    state["port_edges"] = _canonical_port_edges(state.get("port_edges"))

    component = {
        "component_kind": LGRC9V3_EMBEDDED_GRC9V3_STATE_KIND,
        "component_schema_version": (LGRC9V3_EMBEDDED_GRC9V3_STATE_SCHEMA_VERSION),
        "source_model_family": "GRC9V3",
        "source_snapshot_schema": metadata.get("snapshot_schema"),
        "source_snapshot_version": metadata.get("snapshot_version"),
        "resolved_parameter_identity": metadata.get("params_hash"),
        "topology": _canonical_topology(topology),
        "stable_allocation": _stable_allocation(metadata, topology),
        "state": state,
        "base_events": normalized_snapshot.get("events", []),
        "base_observables": normalized_snapshot.get("observables", {}),
        "included_state_groups": list(_INCLUDED_STATE_GROUPS),
        "excluded_representation_fields": list(_EXCLUDED_REPRESENTATION_FIELDS),
    }
    return dict(canonicalize_json_value(component))


def _normalized_embedded_grc9v3_model(
    snapshot: Mapping[str, Any],
) -> GRC9V3:
    caches = _require_mapping(snapshot.get("caches"), context="LGRC9V3 snapshot caches")
    base_snapshot = _require_mapping(
        caches.get("base_grc9v3_snapshot"),
        context="LGRC9V3 snapshot caches.base_grc9v3_snapshot",
    )
    try:
        return GRC9V3._from_snapshot(deepcopy(base_snapshot))
    except SnapshotCompatibilityError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise SnapshotCompatibilityError(
            "embedded GRC9V3 snapshot could not be normalized"
        ) from exc


def digest_lgrc9v3_embedded_grc9v3_state_v1(
    snapshot: Mapping[str, Any],
) -> str:
    """Digest the internal embedded-state component canonically."""

    return digest_canonical_data(build_lgrc9v3_embedded_grc9v3_state_v1(snapshot))


def _lgrc9v3_snapshot(
    source: Mapping[str, Any] | GRCModel,
) -> Mapping[str, Any]:
    if isinstance(source, Mapping):
        return source

    # Avoid coupling LGRC9V3 runtime construction to this optional identity
    # module while still accepting the concrete model at the public boundary.
    from .lgrc_9_v3_runtime import LGRC9V3

    if isinstance(source, LGRC9V3):
        return source.snapshot()
    raise SnapshotCompatibilityError(
        "LGRC9V3 restoration identity source must be an LGRC9V3 model or snapshot"
    )


def lgrc9v3_restoration_identity_v1(
    source: Mapping[str, Any] | GRCModel,
) -> dict[str, Any]:
    """Build the public version-1 LGRC9V3 restoration identity artifact."""

    snapshot = _lgrc9v3_snapshot(source)
    require_snapshot_family(snapshot, expected_family="LGRC9V3")
    metadata = _require_mapping(
        snapshot.get("metadata"),
        context="LGRC9V3 snapshot metadata",
    )
    dynamics = _require_mapping(
        snapshot.get("dynamics"),
        context="LGRC9V3 snapshot dynamics",
    )
    runtime_artifact = _require_mapping(
        dynamics.get("lgrc9v3_runtime"),
        context="LGRC9V3 snapshot dynamics.lgrc9v3_runtime",
    )
    normalized_base_model = _normalized_embedded_grc9v3_model(snapshot)
    normalized_runtime_artifact = restore_lgrc9v3_runtime_state_artifact(
        runtime_artifact,
        base_state=normalized_base_model.get_state(),
    ).to_artifact()
    events = snapshot.get("events")
    if events is None:
        raise SnapshotCompatibilityError("LGRC9V3 snapshot events are required")
    if not isinstance(events, list):
        raise SnapshotCompatibilityError("LGRC9V3 snapshot events must be a list")
    observables = _require_mapping(
        snapshot.get("observables"),
        context="LGRC9V3 snapshot observables",
    )

    artifact = {
        "artifact_kind": LGRC9V3_RESTORATION_IDENTITY_KIND,
        "artifact_schema_version": LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION,
        "model_family": "LGRC9V3",
        "source_snapshot_schema": metadata.get("snapshot_schema"),
        "source_snapshot_version": metadata.get("snapshot_version"),
        "embedded_grc9v3_state": build_lgrc9v3_embedded_grc9v3_state_v1(snapshot),
        "lgrc9v3_runtime_artifact": normalized_runtime_artifact,
        "events": deepcopy(events),
        "observables": deepcopy(observables),
        "included_state_groups": list(_COMPOSITE_INCLUDED_STATE_GROUPS),
        "excluded_representation_fields": list(
            _COMPOSITE_EXCLUDED_REPRESENTATION_FIELDS
        ),
    }
    return dict(canonicalize_json_value(artifact))


def digest_lgrc9v3_restoration_identity_v1(
    source: Mapping[str, Any] | GRCModel,
) -> str:
    """Digest the public version-1 LGRC9V3 restoration identity artifact."""

    return digest_canonical_data(lgrc9v3_restoration_identity_v1(source))


__all__ = [
    "LGRC9V3_EMBEDDED_GRC9V3_STATE_KIND",
    "LGRC9V3_EMBEDDED_GRC9V3_STATE_SCHEMA_VERSION",
    "LGRC9V3_RESTORATION_IDENTITY_KIND",
    "LGRC9V3_RESTORATION_IDENTITY_SCHEMA_VERSION",
    "build_lgrc9v3_embedded_grc9v3_state_v1",
    "digest_lgrc9v3_embedded_grc9v3_state_v1",
    "digest_lgrc9v3_restoration_identity_v1",
    "lgrc9v3_restoration_identity_v1",
]
