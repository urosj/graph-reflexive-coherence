"""Checkpoint export helpers for graph-visible GRCV3 telemetry."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from pygrc.core import BACKEND_SELECTIONS_KEY

from .grc_v3 import GRCV3

if TYPE_CHECKING:
    from pygrc.telemetry.schema import GraphCheckpointArtifact, RunTelemetryIdentity


GRCV3_CHECKPOINT_CONTRACT_VERSION = "phase_t_iter26_v1"


def export_grcv3_graph_checkpoint(
    model: GRCV3,
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
    """Export one deterministic graph checkpoint from the current GRCV3 state."""

    from pygrc.telemetry import GraphCheckpointArtifact

    state = model.get_state()
    topology = state.topology
    label_computation_modes = dict(
        state.cached_quantities.get(
            "edge_label_computation_mode",
            state.edge_label_computation_mode,
        )
    )

    node_records: list[dict[str, Any]] = []
    any_chart_hints = False
    choice_registry = state.choice_registry if isinstance(state.choice_registry, Mapping) else {}
    collapse_registry = (
        state.collapse_registry if isinstance(state.collapse_registry, Mapping) else {}
    )
    for node_id in sorted(topology.iter_live_node_ids()):
        attributes = state.nodes[node_id]
        payload = dict(topology.node_payload(node_id))
        gradient = [float(value) for value in attributes.gradient]
        gradient_norm = math.sqrt(sum(value * value for value in gradient))
        hessian = [[float(value) for value in row] for row in attributes.hessian]
        net_flux_vector = [float(value) for value in attributes.net_flux]
        record: dict[str, Any] = {
            "node_id": node_id,
            "coherence": float(attributes.coherence),
            "basin_id": attributes.basin_id,
            "depth": int(attributes.depth),
            "basin_mass": float(attributes.basin_mass),
            "gradient": gradient,
            "gradient_norm": float(gradient_norm),
            "hessian": hessian,
            "net_flux": net_flux_vector,
            "payload": payload,
        }
        if attributes.parent_id is not None:
            record["parent_id"] = attributes.parent_id
        if node_id in state.potential:
            record["potential"] = float(state.potential[node_id])
        if node_id in state.sink_set:
            record["sink_flag"] = True
        node_key = str(node_id)
        collapse_entry = collapse_registry.get(node_key)
        if isinstance(collapse_entry, Mapping):
            record["collapse_flag"] = True
            collapsed_sink_id = collapse_entry.get("collapsed_sink_id")
            if collapsed_sink_id is not None:
                record["collapsed_sink_id"] = collapsed_sink_id
            winner_margin = collapse_entry.get("winner_margin")
            if isinstance(winner_margin, int | float) and not isinstance(winner_margin, bool):
                record["collapse_winner_margin"] = float(winner_margin)
            collapsed_step_index = collapse_entry.get("collapsed_step_index")
            if isinstance(collapsed_step_index, int) and not isinstance(collapsed_step_index, bool):
                record["collapsed_step_index"] = int(collapsed_step_index)
            previous_viable_sink_ids = collapse_entry.get("previous_viable_sink_ids")
            if isinstance(previous_viable_sink_ids, list | tuple):
                record["previous_viable_sink_ids"] = list(previous_viable_sink_ids)
        choice_entry = choice_registry.get(node_key)
        if isinstance(choice_entry, Mapping):
            record["choice_flag"] = True
            viable_sink_ids = choice_entry.get("viable_sink_ids")
            if isinstance(viable_sink_ids, list | tuple):
                record["choice_viable_sink_ids"] = list(viable_sink_ids)
            winner_sink_id = choice_entry.get("winner_sink_id")
            if winner_sink_id is not None:
                record["choice_winner_sink_id"] = winner_sink_id
            winner_margin = choice_entry.get("winner_margin")
            if isinstance(winner_margin, int | float) and not isinstance(winner_margin, bool):
                record["choice_winner_margin"] = float(winner_margin)
        if _has_chart_center_hint(payload):
            any_chart_hints = True

        if include_flow_overlays:
            outgoing_flux_values = [
                float(state.flux.get((edge_id, node_id), 0.0))
                for edge_id in topology.incident_edge_ids(node_id)
            ]
            if outgoing_flux_values:
                out_flux = float(sum(value for value in outgoing_flux_values if value > 0.0))
                in_flux = float(sum(-value for value in outgoing_flux_values if value < 0.0))
                record["net_edge_flux"] = float(sum(outgoing_flux_values))
                record["in_flux"] = in_flux
                record["out_flux"] = out_flux
        node_records.append(record)

    edge_records: list[dict[str, Any]] = []
    any_signed_flux = False
    for edge_id in sorted(topology.iter_live_edge_ids()):
        source_node_id, target_node_id = topology.edge_endpoints(edge_id)
        payload = dict(topology.edge_payload(edge_id))
        record: dict[str, Any] = {
            "edge_id": edge_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "base_conductance": float(state.base_conductance.get(edge_id, 0.0)),
            "payload": payload,
            "geometric_length_available": edge_id in state.geometric_length,
        }
        directionality_semantics = payload.get("directionality_semantics")
        if isinstance(directionality_semantics, str):
            record["directionality_semantics"] = directionality_semantics
        if "geometric_length" in label_computation_modes:
            record["geometric_length_mode"] = label_computation_modes["geometric_length"]
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
        layout_mode="ambient_chart_hint" if any_chart_hints else None,
        layout_dimensions=2 if any_chart_hints else None,
        label_computation_modes=label_computation_modes,
        topology_extensions={
            "next_node_id": topology.next_node_id,
            "next_edge_id": topology.next_edge_id,
        },
        family_extensions={
            "grcv3": {
                "contract_version": GRCV3_CHECKPOINT_CONTRACT_VERSION,
                "params_identity": state.params_identity,
                "budget_target": float(state.budget_target),
                "remainder": float(state.remainder),
                "hessian_sign": _coerce_hessian_sign(
                    state.cached_quantities.get("hessian_sign")
                ),
                "backend_summary": _backend_summary(model),
                "hierarchy_summary": _hierarchy_summary(state),
                "spark_summary": _spark_summary(state),
                "choice_summary": _choice_summary(state),
                **_optional_landscape_context(state.cached_quantities),
            }
        },
    )


def _coerce_hessian_sign(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value in (-1, 1):
        return int(value)
    return None


def _backend_summary(model: GRCV3) -> Mapping[str, Any]:
    backend_payload = dict(model.get_params().constitutive_semantic_modes[BACKEND_SELECTIONS_KEY])
    return {
        "geometry_backend": str(dict(backend_payload["geometry"])["name"]),
        "differential_backend": str(dict(backend_payload["differential_summary"])["name"]),
        "metric_backend": str(dict(backend_payload["metric"])["name"]),
        "spark_backend": str(dict(backend_payload["spark"])["name"]),
        "hierarchy_backend": str(dict(backend_payload["hierarchy_update"])["name"]),
        "choice_backend": str(dict(backend_payload["choice"])["name"]),
    }


def _hierarchy_summary(state: Any) -> Mapping[str, Any]:
    hierarchy_roots = state.cached_quantities.get("hierarchy_roots", [])
    child_basin_link_count = sum(len(children) for children in state.hierarchy.values())
    return {
        "hierarchy_root_count": len(hierarchy_roots) if isinstance(hierarchy_roots, list) else 0,
        "hierarchy_node_count": len(state.hierarchy),
        "child_basin_link_count": int(child_basin_link_count),
    }


def _spark_summary(state: Any) -> Mapping[str, Any]:
    split_registry_raw = state.cached_quantities.get("split_registry", {})
    split_registry = split_registry_raw if isinstance(split_registry_raw, Mapping) else {}
    active_split_count = 0
    confirmed_split_count = 0
    pending_spark_count = 0
    for entry in split_registry.values():
        if not isinstance(entry, Mapping):
            continue
        if bool(entry.get("complete", False)):
            confirmed_split_count += 1
        else:
            active_split_count += 1
        if str(entry.get("status", "")) == "spark_pending":
            pending_spark_count += 1
    return {
        "split_registry_size": len(split_registry),
        "active_split_count": active_split_count,
        "confirmed_split_count": confirmed_split_count,
        "pending_spark_count": pending_spark_count,
    }


def _choice_summary(state: Any) -> Mapping[str, Any]:
    choice_registry = state.choice_registry if isinstance(state.choice_registry, Mapping) else {}
    collapse_registry = (
        state.collapse_registry if isinstance(state.collapse_registry, Mapping) else {}
    )
    evaluated_nodes = 0
    for entry in choice_registry.values():
        if isinstance(entry, Mapping):
            evaluated_nodes += 1
    return {
        "choice_regime_count": len(choice_registry),
        "collapse_registry_count": len(collapse_registry),
        "evaluated_node_count": evaluated_nodes,
    }


def _optional_landscape_context(cached_quantities: Mapping[str, Any]) -> Mapping[str, Any]:
    fields = (
        "landscape_lowering_lane",
        "landscape_lowering_semantic_authority",
        "landscape_runtime_assembly_mode",
    )
    payload = {
        field: cached_quantities[field]
        for field in fields
        if field in cached_quantities
    }
    monitoring_context = _optional_landscape_monitoring_context(cached_quantities)
    if monitoring_context:
        payload.update(monitoring_context)
    return payload


def _optional_landscape_monitoring_context(
    cached_quantities: Mapping[str, Any],
) -> Mapping[str, Any]:
    runtime_summary = cached_quantities.get("landscape_runtime_assembly_summary")
    node_id_by_primitive_id = cached_quantities.get("landscape_node_id_by_primitive_id")
    if not isinstance(runtime_summary, Mapping) or not isinstance(
        node_id_by_primitive_id, Mapping
    ):
        return {}
    monitoring_fields = (
        ("transfer_mediation", "transfer_mediation_primitive_ids"),
        ("interior_load_carriers", "interior_load_carrier_primitive_ids"),
        ("interior_partition", "interior_partition_primitive_ids"),
        ("interior_geometry", "interior_geometry_primitive_ids"),
    )
    for monitoring_surface_kind, ids_field in monitoring_fields:
        primitive_ids = runtime_summary.get(ids_field)
        if not isinstance(primitive_ids, list | tuple) or not primitive_ids:
            continue
        monitored_node_ids_by_primitive_id = {
            str(primitive_id): int(node_id_by_primitive_id[primitive_id])
            for primitive_id in primitive_ids
            if primitive_id in node_id_by_primitive_id
            and isinstance(node_id_by_primitive_id[primitive_id], int)
            and not isinstance(node_id_by_primitive_id[primitive_id], bool)
        }
        if not monitored_node_ids_by_primitive_id:
            continue
        return {
            "landscape_monitoring_surface_kind": monitoring_surface_kind,
            "landscape_monitored_node_ids_by_primitive_id": dict(
                sorted(monitored_node_ids_by_primitive_id.items())
            ),
        }
    return {}


def _has_chart_center_hint(payload: Mapping[str, Any]) -> bool:
    value = payload.get("chart_center_hint")
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(component, int | float) for component in value)
    )


__all__ = [
    "GRCV3_CHECKPOINT_CONTRACT_VERSION",
    "export_grcv3_graph_checkpoint",
]
