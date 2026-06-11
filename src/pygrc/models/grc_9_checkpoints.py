"""Checkpoint export helpers for graph-visible GRC9 telemetry."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from pygrc.telemetry.grc9_contract import GRC9_TELEMETRY_CONTRACT_VERSION

from .grc_9 import GRC9
from .grc_9_ports import port_to_rc, slot_to_port_id

if TYPE_CHECKING:
    from pygrc.telemetry.schema import GraphCheckpointArtifact, RunTelemetryIdentity


def export_grc9_graph_checkpoint(
    model: GRC9,
    *,
    identity: "RunTelemetryIdentity",
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str | None,
    event_step_range: Mapping[str, int],
    event_count_window: int,
    event_counts_by_kind_window: Mapping[str, int],
    include_flow_overlays: bool,
) -> "GraphCheckpointArtifact":
    """Export one deterministic port-graph checkpoint from current GRC9 state."""

    from pygrc.telemetry import GraphCheckpointArtifact

    state = model.get_state()
    topology = state.topology
    module_by_node = _module_membership_by_node(state.expansion_registry)
    basin_by_node = _basin_membership_by_node(state.basins)
    port_overlays: dict[str, list[dict[str, Any]]] = {}

    node_records: list[dict[str, Any]] = []
    for node_id in sorted(topology.iter_live_node_ids()):
        row_occupancy = [0, 0, 0]
        column_occupancy = [0, 0, 0]
        node_ports: list[dict[str, Any]] = []
        for slot in topology.iter_port_slots(node_id):
            port_id = slot_to_port_id(int(slot))
            row, column = port_to_rc(port_id)
            edge_id = topology.port_edge_id(node_id, int(slot))
            occupied = edge_id is not None
            if occupied:
                row_occupancy[row - 1] += 1
                column_occupancy[column - 1] += 1
            node_ports.append(
                {
                    "port_id": port_id,
                    "slot": int(slot),
                    "row": row,
                    "column": column,
                    "occupied": occupied,
                    "incident_edge_id": edge_id,
                }
            )
        port_overlays[str(node_id)] = node_ports
        record: dict[str, Any] = {
            "node_id": node_id,
            "coherence": float(state.node_coherence.get(node_id, 0.0)),
            "potential": float(state.potential.get(node_id, 0.0)),
            "active_degree": len(tuple(topology.incident_edge_ids(node_id))),
            "row_occupancy": row_occupancy,
            "column_occupancy": column_occupancy,
            "sink_flag": node_id in state.sink_set,
            "payload": dict(topology.node_payload(node_id)),
        }
        basin_sink_id = basin_by_node.get(node_id)
        if basin_sink_id is not None:
            record["basin_sink_id"] = basin_sink_id
        module_membership = module_by_node.get(node_id)
        if module_membership is not None:
            record["module_id"] = module_membership["module_id"]
            record["module_role"] = module_membership["module_role"]
            record["module_parent_sink_id"] = module_membership["parent_sink_id"]
        node_records.append(record)

    module_overlays = _module_overlays(state.expansion_registry, topology)
    latest_reassignments = _latest_reassignment_overlays(
        state.cached_quantities.get("last_expansion", {})
    )
    internal_edge_ids = {
        edge_id
        for module_payload in module_overlays.values()
        for edge_id in module_payload["internal_edge_ids"]
    }
    reassigned_edge_ids = {
        int(edge_id)
        for edge_ids in latest_reassignments.values()
        for edge_id in edge_ids
    }

    edge_records: list[dict[str, Any]] = []
    any_signed_flux = False
    for edge_id in sorted(topology.iter_live_edge_ids()):
        endpoint_a, endpoint_b = topology.edge_ports(edge_id)
        source_node_id, source_slot = endpoint_a
        target_node_id, target_slot = endpoint_b
        source_port_id = slot_to_port_id(source_slot)
        target_port_id = slot_to_port_id(target_slot)
        port_edge = state.port_edges.get(edge_id)
        signed_flux = 0.0 if port_edge is None else float(port_edge.flux_uv)
        record: dict[str, Any] = {
            "edge_id": edge_id,
            "source_node_id": source_node_id,
            "source_port_id": source_port_id,
            "target_node_id": target_node_id,
            "target_port_id": target_port_id,
            "conductance": 0.0 if port_edge is None else float(port_edge.conductance),
            "payload": dict(topology.edge_payload(edge_id)),
            "internal_module_edge": edge_id in internal_edge_ids,
            "reassigned_boundary_edge": edge_id in reassigned_edge_ids,
            "geometric_length_available": edge_id in state.geometric_length,
            "temporal_delay_available": edge_id in state.temporal_delay,
            "flux_coupling_available": edge_id in state.flux_coupling,
        }
        if edge_id in state.geometric_length:
            record["geometric_length"] = float(state.geometric_length[edge_id])
        if edge_id in state.temporal_delay:
            record["temporal_delay"] = float(state.temporal_delay[edge_id])
        if edge_id in state.flux_coupling:
            record["flux_coupling"] = float(state.flux_coupling[edge_id])
        if include_flow_overlays:
            record["signed_flux"] = signed_flux
            record["signed_flux_source"] = signed_flux
            record["signed_flux_target"] = -signed_flux
            record["flux_orientation_source_node_id"] = source_node_id
            record["flux_orientation_target_node_id"] = target_node_id
            record["flux_symmetry"] = "antisymmetric"
            any_signed_flux = any_signed_flux or signed_flux != 0.0
        edge_records.append(record)

    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=state.step_index,
        time=float(state.time),
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        graph_kind="port_graph",
        node_count=len(node_records),
        edge_count=len(edge_records),
        node_records=tuple(node_records),
        edge_records=tuple(edge_records),
        event_step_range=event_step_range,
        event_count_window=event_count_window,
        event_counts_by_kind_window=event_counts_by_kind_window,
        flow_representation=(
            "signed_edge_flux"
            if include_flow_overlays and any_signed_flux
            else ("zero_signed_edge_flux" if include_flow_overlays else None)
        ),
        flow_cadence="checkpoint_only" if include_flow_overlays else None,
        layout_mode="fixed_nine_slot_port_chart",
        layout_dimensions=2,
        label_computation_modes=_label_computation_modes(model),
        topology_extensions={
            "next_node_id": topology.next_node_id,
            "next_edge_id": topology.next_edge_id,
        },
        family_extensions={
            "grc9": {
                "contract_version": GRC9_TELEMETRY_CONTRACT_VERSION,
                "checkpoint_payload": "port_chart_module_overlay_v1",
                "params_identity": state.params_identity,
                "budget_target": float(state.budget_target),
                "remainder": float(state.remainder),
                "port_overlays": port_overlays,
                "module_overlays": module_overlays,
                "latest_reassigned_boundary_edges_by_column": latest_reassignments,
            }
        },
    )


def _module_membership_by_node(expansion_registry: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    membership: dict[int, dict[str, Any]] = {}
    for expansion_id, record in sorted(expansion_registry.items()):
        module_node_ids = tuple(record.module_node_ids)
        for index, node_id in enumerate(module_node_ids):
            if index == 0:
                role = "core"
            elif 1 <= index <= 3:
                role = "satellite"
            else:
                role = "helper"
            membership[node_id] = {
                "module_id": str(expansion_id),
                "module_role": role,
                "parent_sink_id": int(record.parent_sink_id),
            }
    return membership


def _basin_membership_by_node(basins: Mapping[int, set[int]]) -> dict[int, int]:
    membership: dict[int, int] = {}
    for sink_id, members in sorted(basins.items()):
        for node_id in sorted(members):
            membership[node_id] = int(sink_id)
    return membership


def _module_overlays(expansion_registry: Mapping[str, Any], topology: Any) -> dict[str, dict[str, Any]]:
    overlays: dict[str, dict[str, Any]] = {}
    for expansion_id, record in sorted(expansion_registry.items()):
        module_node_ids = tuple(int(node_id) for node_id in record.module_node_ids)
        module_node_set = set(module_node_ids)
        internal_edge_ids: list[int] = []
        for edge_id in sorted(topology.iter_live_edge_ids()):
            endpoint_a, endpoint_b = topology.edge_ports(edge_id)
            payload = dict(topology.edge_payload(edge_id))
            if (
                endpoint_a[0] in module_node_set
                and endpoint_b[0] in module_node_set
                and payload.get("kind") == "expansion_internal"
            ):
                internal_edge_ids.append(edge_id)
        overlays[str(expansion_id)] = {
            "parent_sink_id": int(record.parent_sink_id),
            "core_node_id": module_node_ids[0] if module_node_ids else None,
            "satellite_node_ids": list(module_node_ids[1:4]),
            "helper_node_ids": list(module_node_ids[4:]),
            "module_node_ids": list(module_node_ids),
            "internal_edge_ids": internal_edge_ids,
            "distribution_weights": [float(value) for value in record.distribution_weights],
        }
    return overlays


def _latest_reassignment_overlays(value: Any) -> dict[str, list[int]]:
    if not isinstance(value, Mapping):
        return {}
    reassignment_map = value.get("reassignment_map", {})
    if not isinstance(reassignment_map, Mapping):
        return {}
    by_column: dict[str, list[int]] = {}
    for raw_edge_id, raw_payload in reassignment_map.items():
        if not isinstance(raw_payload, Mapping):
            continue
        try:
            edge_id = int(raw_edge_id)
            from_port_id = int(raw_payload.get("from_port_id"))
        except (TypeError, ValueError):
            continue
        column = ((from_port_id - 1) % 3) + 1
        by_column.setdefault(str(column), []).append(edge_id)
    return {
        column: sorted(edge_ids)
        for column, edge_ids in sorted(by_column.items(), key=lambda item: int(item[0]))
    }


def _label_computation_modes(model: GRC9) -> dict[str, str]:
    state = model.get_state()
    cached_modes = state.cached_quantities.get("edge_label_computation_mode")
    if isinstance(cached_modes, Mapping):
        return {str(key): str(value) for key, value in sorted(cached_modes.items())}
    return {
        str(key): str(value)
        for key, value in sorted(state.edge_label_computation_mode.items())
    }


__all__ = ["export_grc9_graph_checkpoint"]
