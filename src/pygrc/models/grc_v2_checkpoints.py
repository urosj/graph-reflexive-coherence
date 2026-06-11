"""Checkpoint export helpers for graph-visible GRCV2 telemetry."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from .grc_v2 import GRCV2

if TYPE_CHECKING:
    from pygrc.telemetry.schema import GraphCheckpointArtifact, RunTelemetryIdentity


def export_grcv2_graph_checkpoint(
    model: GRCV2,
    *,
    identity: RunTelemetryIdentity,
    checkpoint_id: str,
    checkpoint_label: str,
    checkpoint_reason: str | None,
    event_step_range: Mapping[str, int],
    event_count_window: int,
    event_counts_by_kind_window: Mapping[str, int],
    include_flow_overlays: bool,
) -> GraphCheckpointArtifact:
    """Export one deterministic graph checkpoint from the current GRCV2 state."""

    from pygrc.telemetry import GraphCheckpointArtifact

    state = model.get_state()
    topology = state.topology
    label_computation_modes = dict(state.cached_quantities.get("edge_label_computation_mode", {}))
    landscape_base_edge_conductance = dict(
        state.cached_quantities.get("landscape_base_edge_conductance", {})
    )
    landscape_transport_intent_multiplier = dict(
        state.cached_quantities.get("landscape_transport_intent_multiplier", {})
    )
    sink_to_basin_id: dict[int, int] = {}
    for sink_node_id, basin_members in state.basins.items():
        for basin_member in basin_members:
            sink_to_basin_id[basin_member] = sink_node_id

    node_records: list[dict[str, Any]] = []
    for node_id in sorted(topology.iter_live_node_ids()):
        outgoing_flux_values = [
            float(state.flux.get((edge_id, node_id), 0.0))
            for edge_id in topology.incident_edge_ids(node_id)
        ]
        out_flux = float(sum(value for value in outgoing_flux_values if value > 0.0))
        in_flux = float(sum(-value for value in outgoing_flux_values if value < 0.0))
        record: dict[str, Any] = {
            "node_id": node_id,
            "coherence": float(state.nodes.get(node_id, 0.0)),
            "payload": dict(topology.node_payload(node_id)),
        }
        if node_id in state.potential:
            record["potential"] = float(state.potential[node_id])
        if node_id in state.sink_set:
            record["sink_flag"] = True
        if node_id in sink_to_basin_id:
            record["basin_id"] = sink_to_basin_id[node_id]
        payload = topology.node_payload(node_id)
        if "parent_id" in payload and payload["parent_id"] is not None:
            record["parent_id"] = payload["parent_id"]
        if include_flow_overlays and outgoing_flux_values:
            record["net_flux"] = float(sum(outgoing_flux_values))
            record["in_flux"] = in_flux
            record["out_flux"] = out_flux
        node_records.append(record)

    edge_records: list[dict[str, Any]] = []
    any_signed_flux = False
    for edge_id in sorted(topology.iter_live_edge_ids()):
        source_node_id, target_node_id = topology.edge_endpoints(edge_id)
        record = {
            "edge_id": edge_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "base_conductance": float(state.edges.get(edge_id, 0.0)),
            "payload": dict(topology.edge_payload(edge_id)),
            "geometric_length_available": edge_id in state.geometric_length,
        }
        if edge_id in landscape_base_edge_conductance:
            record["landscape_base_conductance"] = float(landscape_base_edge_conductance[edge_id])
        if edge_id in landscape_transport_intent_multiplier:
            record["transport_intent_multiplier"] = float(
                landscape_transport_intent_multiplier[edge_id]
            )
        if "geometric_length" in label_computation_modes:
            record["geometric_length_mode"] = label_computation_modes["geometric_length"]
        directionality_semantics = topology.edge_payload(edge_id).get("directionality_semantics")
        if isinstance(directionality_semantics, str):
            record["directionality_semantics"] = directionality_semantics
        if edge_id in state.geometric_length:
            record["geometric_length"] = float(state.geometric_length[edge_id])
        if edge_id in state.temporal_delay:
            record["temporal_delay"] = float(state.temporal_delay[edge_id])
        if edge_id in state.flux_coupling:
            record["flux_coupling"] = float(state.flux_coupling[edge_id])
        if include_flow_overlays and (edge_id, source_node_id) in state.flux:
            signed_flux_source = float(state.flux[(edge_id, source_node_id)])
            record["signed_flux"] = signed_flux_source
            record["signed_flux_source"] = signed_flux_source
            record["signed_flux_target"] = float(-signed_flux_source)
            record["flux_orientation_source_node_id"] = source_node_id
            record["flux_orientation_target_node_id"] = target_node_id
            record["flux_symmetry"] = "antisymmetric"
            any_signed_flux = True
        edge_records.append(record)

    flow_representation: str | None = None
    if include_flow_overlays:
        flow_representation = (
            "signed_edge_flux" if any_signed_flux else "not_available_pre_step"
        )

    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=state.step_index,
        time=float(state.time),
        checkpoint_label=checkpoint_label,
        checkpoint_reason=checkpoint_reason,
        graph_kind="weighted_graph",
        node_count=len(node_records),
        edge_count=len(edge_records),
        node_records=tuple(node_records),
        edge_records=tuple(edge_records),
        event_step_range=event_step_range,
        event_count_window=event_count_window,
        event_counts_by_kind_window=event_counts_by_kind_window,
        flow_representation=flow_representation,
        flow_cadence="checkpoint_only" if include_flow_overlays else None,
        label_computation_modes=label_computation_modes,
        topology_extensions={
            "next_node_id": topology.next_node_id,
            "next_edge_id": topology.next_edge_id,
        },
        family_extensions={
            "grcv2": {
                "params_identity": state.params_identity,
                "budget_target": float(state.budget_target),
                "remainder": float(state.remainder),
                "mass_scale": float(state.cached_quantities.get("landscape_mass_scale", 1.0)),
                "budget_mode": state.cached_quantities.get("landscape_budget_mode"),
                "seed_validation_mode": state.cached_quantities.get(
                    "landscape_seed_validation_mode"
                ),
            }
        },
    )


__all__ = ["export_grcv2_graph_checkpoint"]
