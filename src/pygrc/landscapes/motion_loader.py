"""Artifact/window loader for motion inference."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference_loader import (
    LandscapeInferenceArtifactLoadResult,
    load_landscape_inference_artifacts,
)
from .inference_substrate import (
    LandscapeInferenceCheckpointGraph,
    LandscapeInferenceEvidenceSubstrate,
    build_landscape_inference_evidence_substrate,
)
from .motion import (
    MotionCheckpointSpacing,
    MotionWindow,
)


@dataclass(frozen=True)
class MotionWindowAvailability:
    """Motion-window availability/degradation summary."""

    checkpoint_series_available: bool
    checkpoint_count: int
    local_motion_claim_status: str
    diagnostic_only: bool
    missing_surfaces: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return {
            "checkpoint_series_available": self.checkpoint_series_available,
            "checkpoint_count": int(self.checkpoint_count),
            "local_motion_claim_status": self.local_motion_claim_status,
            "diagnostic_only": self.diagnostic_only,
            "missing_surfaces": list(self.missing_surfaces),
        }


@dataclass(frozen=True)
class MotionCheckpointNodeEvidence:
    """Compact per-checkpoint node evidence for motion observers."""

    node_id: int
    coherence: float | None
    basin_id: str | None
    basin_mass: float | None
    sink_flag: bool
    representative_modes: tuple[str, ...]
    continuity_delta: float | None
    successor_node_id: int | None
    hierarchy_parent_id: str | None
    provenance_tokens: tuple[str, ...]
    coordinates: tuple[float, ...] | None
    provenance_available: bool
    port_matrix_available: bool

    def to_mapping(self) -> dict[str, Any]:
        return {
            "node_id": int(self.node_id),
            "coherence": self.coherence,
            "basin_id": self.basin_id,
            "basin_mass": self.basin_mass,
            "sink_flag": self.sink_flag,
            "representative_modes": list(self.representative_modes),
            "continuity_delta": self.continuity_delta,
            "successor_node_id": self.successor_node_id,
            "hierarchy_parent_id": self.hierarchy_parent_id,
            "provenance_tokens": list(self.provenance_tokens),
            "coordinates": None if self.coordinates is None else list(self.coordinates),
            "provenance_available": self.provenance_available,
            "port_matrix_available": self.port_matrix_available,
        }


@dataclass(frozen=True)
class MotionCheckpointEdgeEvidence:
    """Compact per-checkpoint edge evidence for motion observers."""

    edge_id: int
    source_node_id: int
    target_node_id: int
    signed_flux: float | None
    conductance: float | None
    provenance_available: bool
    is_bridge: bool

    def to_mapping(self) -> dict[str, Any]:
        return {
            "edge_id": int(self.edge_id),
            "source_node_id": int(self.source_node_id),
            "target_node_id": int(self.target_node_id),
            "signed_flux": self.signed_flux,
            "conductance": self.conductance,
            "provenance_available": self.provenance_available,
            "is_bridge": self.is_bridge,
        }


@dataclass(frozen=True)
class MotionCheckpointEvidence:
    """Compact normalized evidence for one checkpoint in a motion window."""

    checkpoint_id: str
    step_index: int
    time: float | None
    nodes: Mapping[int, MotionCheckpointNodeEvidence]
    edges: Mapping[int, MotionCheckpointEdgeEvidence]
    representative_node_ids: tuple[int, ...]
    centroid_candidate_available: bool
    graph_medoid_proxy_available: bool
    port_matrix_available: bool
    provenance_available: bool

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "checkpoint_id": self.checkpoint_id,
                "step_index": int(self.step_index),
                "time": self.time,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "representative_node_ids": list(self.representative_node_ids),
                "centroid_candidate_available": self.centroid_candidate_available,
                "graph_medoid_proxy_available": self.graph_medoid_proxy_available,
                "port_matrix_available": self.port_matrix_available,
                "provenance_available": self.provenance_available,
            }
        )


@dataclass(frozen=True)
class MotionTopologyDelta:
    """Node/edge birth-removal summary between adjacent checkpoints."""

    from_checkpoint_id: str
    to_checkpoint_id: str
    from_step: int
    to_step: int
    born_node_ids: tuple[int, ...] = ()
    removed_node_ids: tuple[int, ...] = ()
    born_edge_ids: tuple[int, ...] = ()
    removed_edge_ids: tuple[int, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return {
            "from_checkpoint_id": self.from_checkpoint_id,
            "to_checkpoint_id": self.to_checkpoint_id,
            "from_step": int(self.from_step),
            "to_step": int(self.to_step),
            "born_node_ids": [int(value) for value in self.born_node_ids],
            "removed_node_ids": [int(value) for value in self.removed_node_ids],
            "born_edge_ids": [int(value) for value in self.born_edge_ids],
            "removed_edge_ids": [int(value) for value in self.removed_edge_ids],
        }


@dataclass(frozen=True)
class MotionWindowLoadResult:
    """Loaded telemetry/checkpoint evidence normalized for motion inference."""

    artifact_root: Path
    landscape_load_result: LandscapeInferenceArtifactLoadResult
    evidence_substrate: LandscapeInferenceEvidenceSubstrate
    motion_window: MotionWindow
    quadrature_mode: str
    availability: MotionWindowAvailability
    checkpoint_evidence: tuple[MotionCheckpointEvidence, ...]
    topology_deltas: tuple[MotionTopologyDelta, ...]

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "artifact_root": str(self.artifact_root),
                "source_runtime_family": self.landscape_load_result.source_runtime_family,
                "motion_window": self.motion_window.to_mapping(),
                "quadrature_mode": self.quadrature_mode,
                "availability": self.availability.to_mapping(),
                "checkpoint_count": len(self.checkpoint_evidence),
                "topology_delta_count": len(self.topology_deltas),
                "diagnostic_only": self.availability.diagnostic_only,
                "checkpoint_summaries": [
                    checkpoint.to_summary_mapping()
                    for checkpoint in self.checkpoint_evidence
                ],
                "topology_deltas": [delta.to_mapping() for delta in self.topology_deltas],
            }
        )


def load_motion_window(
    path: str | Path,
    *,
    window_policy: str = "whole_run",
    start_step: int | None = None,
    end_step: int | None = None,
    final_step_count: int | None = None,
    event_step: int | None = None,
    radius: int | None = None,
    allow_short_persistence_window: bool = False,
) -> MotionWindowLoadResult:
    """Load one telemetry run and normalize checkpoint evidence for motion."""

    load_result = load_landscape_inference_artifacts(
        path,
        window_policy=window_policy,
        start_step=start_step,
        end_step=end_step,
        final_step_count=final_step_count,
        event_step=event_step,
        radius=radius,
    )
    substrate = build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=allow_short_persistence_window,
    )
    checkpoints_by_id = {
        str(checkpoint.checkpoint_id): checkpoint
        for checkpoint in load_result.telemetry_pack.graph_checkpoints
    }
    ordered_graphs = tuple(sorted(substrate.checkpoint_graphs, key=lambda graph: graph.step_index))
    checkpoint_ids = tuple(graph.checkpoint_id for graph in ordered_graphs)
    selected_checkpoints = tuple(
        checkpoints_by_id[checkpoint_id]
        for checkpoint_id in checkpoint_ids
        if checkpoint_id in checkpoints_by_id
    )
    motion_window = MotionWindow(
        start_step=load_result.inference_window.start_step,
        end_step=load_result.inference_window.end_step,
        checkpoint_ids=checkpoint_ids,
        policy=load_result.inference_window.policy,
        checkpoint_spacing=_checkpoint_spacing(selected_checkpoints),
    )
    checkpoint_evidence = tuple(
        _checkpoint_evidence(graph, checkpoints_by_id.get(graph.checkpoint_id))
        for graph in ordered_graphs
    )
    topology_deltas = _topology_deltas(checkpoint_evidence)
    availability = _motion_availability(
        checkpoint_count=len(checkpoint_evidence),
        diagnostic_only=substrate.diagnostic_only,
        graph_checkpoint_index_available=load_result.availability.graph_checkpoint_index_available,
    )
    return MotionWindowLoadResult(
        artifact_root=load_result.artifact_root,
        landscape_load_result=load_result,
        evidence_substrate=substrate,
        motion_window=motion_window,
        quadrature_mode=_quadrature_mode(substrate),
        availability=availability,
        checkpoint_evidence=checkpoint_evidence,
        topology_deltas=topology_deltas,
    )


def _motion_availability(
    *,
    checkpoint_count: int,
    diagnostic_only: bool,
    graph_checkpoint_index_available: bool,
) -> MotionWindowAvailability:
    missing: list[str] = []
    if not graph_checkpoint_index_available:
        missing.append("graph_checkpoint_index")
    if checkpoint_count == 0:
        missing.append("checkpoint_series")
    if checkpoint_count >= 2 and not diagnostic_only:
        status = "available"
    elif checkpoint_count >= 2:
        status = "diagnostic_only"
    elif checkpoint_count == 1:
        status = "single_checkpoint_unavailable_for_motion"
    else:
        status = "unavailable"
    return MotionWindowAvailability(
        checkpoint_series_available=checkpoint_count >= 2,
        checkpoint_count=checkpoint_count,
        local_motion_claim_status=status,
        diagnostic_only=diagnostic_only or checkpoint_count < 2,
        missing_surfaces=tuple(missing),
    )


def _checkpoint_evidence(
    graph: LandscapeInferenceCheckpointGraph,
    checkpoint: Any | None,
) -> MotionCheckpointEvidence:
    max_coherence = _max_coherence(graph)
    node_evidence = {
        node_id: _node_evidence(node, max_coherence=max_coherence)
        for node_id, node in graph.nodes.items()
    }
    edge_evidence = {
        edge_id: MotionCheckpointEdgeEvidence(
            edge_id=edge.edge_id,
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            signed_flux=edge.signed_flux,
            conductance=edge.conductance,
            provenance_available=bool(edge.provenance),
            is_bridge=edge.is_bridge,
        )
        for edge_id, edge in graph.edges.items()
    }
    representative_node_ids = tuple(
        sorted(
            node_id
            for node_id, node in node_evidence.items()
            if node.representative_modes
        )
    )
    return MotionCheckpointEvidence(
        checkpoint_id=graph.checkpoint_id,
        step_index=graph.step_index,
        time=None if checkpoint is None else float(checkpoint.time),
        nodes=node_evidence,
        edges=edge_evidence,
        representative_node_ids=representative_node_ids,
        centroid_candidate_available=any(
            node.coordinates is not None for node in node_evidence.values()
        ),
        graph_medoid_proxy_available=bool(node_evidence),
        port_matrix_available=graph.port_matrix_available,
        provenance_available=graph.provenance_available,
    )


def _node_evidence(
    node: Any,
    *,
    max_coherence: float | None,
) -> MotionCheckpointNodeEvidence:
    modes: list[str] = []
    if node.sink_flag:
        modes.append("sink")
    if (
        node.coherence is not None
        and max_coherence is not None
        and math.isclose(float(node.coherence), max_coherence, rel_tol=0.0, abs_tol=1e-12)
    ):
        modes.append("peak_coherence")
    if node.port_matrix is not None:
        modes.append("port_front_candidate")
    return MotionCheckpointNodeEvidence(
        node_id=node.node_id,
        coherence=node.coherence,
        basin_id=node.basin_id,
        basin_mass=node.basin_mass,
        sink_flag=node.sink_flag,
        representative_modes=tuple(modes),
        continuity_delta=_optional_float_from_keys(
            node.payload,
            ("continuity_delta", "coherence_delta", "last_continuity_delta"),
        ),
        successor_node_id=_optional_int_from_keys(
            node.payload,
            ("successor_node_id", "successor", "successor_id"),
        ),
        hierarchy_parent_id=_optional_string_from_keys(
            node.payload,
            ("hierarchy_parent", "hierarchy_parent_id", "parent_id"),
        ),
        provenance_tokens=_provenance_tokens(node.provenance),
        coordinates=_coordinates_from_payload(node.payload),
        provenance_available=bool(node.provenance),
        port_matrix_available=node.port_matrix is not None,
    )


def _max_coherence(graph: LandscapeInferenceCheckpointGraph) -> float | None:
    values = tuple(
        float(node.coherence)
        for node in graph.nodes.values()
        if node.coherence is not None
    )
    if not values:
        return None
    return max(values)


def _topology_deltas(
    checkpoints: Sequence[MotionCheckpointEvidence],
) -> tuple[MotionTopologyDelta, ...]:
    deltas: list[MotionTopologyDelta] = []
    for previous, current in zip(checkpoints, checkpoints[1:]):
        previous_nodes = set(previous.nodes)
        current_nodes = set(current.nodes)
        previous_edges = set(previous.edges)
        current_edges = set(current.edges)
        deltas.append(
            MotionTopologyDelta(
                from_checkpoint_id=previous.checkpoint_id,
                to_checkpoint_id=current.checkpoint_id,
                from_step=previous.step_index,
                to_step=current.step_index,
                born_node_ids=tuple(sorted(current_nodes - previous_nodes)),
                removed_node_ids=tuple(sorted(previous_nodes - current_nodes)),
                born_edge_ids=tuple(sorted(current_edges - previous_edges)),
                removed_edge_ids=tuple(sorted(previous_edges - current_edges)),
            )
        )
    return tuple(deltas)


def _checkpoint_spacing(checkpoints: Sequence[Any]) -> MotionCheckpointSpacing:
    if len(checkpoints) < 2:
        return MotionCheckpointSpacing(spacing_mode="unknown")
    ordered = tuple(sorted(checkpoints, key=lambda checkpoint: int(checkpoint.step_index)))
    step_deltas = tuple(
        int(current.step_index) - int(previous.step_index)
        for previous, current in zip(ordered, ordered[1:])
    )
    time_deltas = tuple(
        float(current.time) - float(previous.time)
        for previous, current in zip(ordered, ordered[1:])
    )
    if not time_deltas:
        mode = "ordinal_only"
    elif len(set(step_deltas)) <= 1 and _float_values_equal(time_deltas):
        mode = "regular"
    else:
        mode = "irregular"
    return MotionCheckpointSpacing(
        spacing_mode=mode,
        step_deltas=step_deltas,
        time_deltas=time_deltas,
    )


def _quadrature_mode(substrate: LandscapeInferenceEvidenceSubstrate) -> str:
    modes = tuple(
        graph.budget_audit.quadrature_weight_mode
        for graph in substrate.checkpoint_graphs
    )
    if not modes:
        return "unavailable"
    if "checkpoint_weight" in modes:
        return "checkpoint_weight"
    if "unit_measure" in modes:
        return "unit_measure"
    if "unit_measure_assumed" in modes:
        return "unit_measure_assumed"
    return "unavailable"


def _coordinates_from_payload(payload: Mapping[str, Any]) -> tuple[float, ...] | None:
    for key in ("coordinates", "position", "chart_position", "chart_center", "center"):
        value = payload.get(key)
        if not isinstance(value, Sequence) or isinstance(value, str | bytes):
            continue
        coordinates: list[float] = []
        for item in value:
            if isinstance(item, bool) or not isinstance(item, int | float):
                coordinates = []
                break
            number = float(item)
            if not math.isfinite(number):
                coordinates = []
                break
            coordinates.append(number)
        if coordinates:
            return tuple(coordinates)
    return None


def _optional_float_from_keys(
    payload: Mapping[str, Any],
    keys: Sequence[str],
) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, int | float):
            continue
        number = float(value)
        if math.isfinite(number):
            return number
    return None


def _optional_int_from_keys(
    payload: Mapping[str, Any],
    keys: Sequence[str],
) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        return int(value)
    return None


def _optional_string_from_keys(
    payload: Mapping[str, Any],
    keys: Sequence[str],
) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _provenance_tokens(provenance: Mapping[str, Any]) -> tuple[str, ...]:
    tokens: list[str] = []
    for key, value in sorted(provenance.items()):
        if isinstance(value, str) and value.strip():
            tokens.append(f"{key}:{value}")
        elif isinstance(value, int) and not isinstance(value, bool):
            tokens.append(f"{key}:{value}")
    return tuple(tokens)


def _float_values_equal(values: Sequence[float]) -> bool:
    if not values:
        return True
    first = float(values[0])
    return all(math.isclose(first, float(value), rel_tol=0.0, abs_tol=1e-12) for value in values)


__all__ = [
    "MotionCheckpointEdgeEvidence",
    "MotionCheckpointEvidence",
    "MotionCheckpointNodeEvidence",
    "MotionTopologyDelta",
    "MotionWindowAvailability",
    "MotionWindowLoadResult",
    "load_motion_window",
]
