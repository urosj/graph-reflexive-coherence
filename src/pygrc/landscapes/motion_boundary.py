"""Boundary/frontier-motion observer over normalized motion windows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .motion import (
    MotionCarrierSet,
    MotionEvidence,
    MotionRecord,
    MotionReport,
)
from .motion_loader import MotionWindowLoadResult, load_motion_window
from .inference_substrate import (
    LandscapeInferenceCheckpointGraph,
    LandscapeInferenceNodeEvidence,
)


BOUNDARY_MOTION_CLASSIFIER_ID = "motion_boundary_frontier_observer"
BOUNDARY_MOTION_CLASSIFIER_VERSION = "motion_inference_iter6_v1"

_RIDGE_GRADIENT_THRESHOLD = 1.0
_RIDGE_TENSOR_ANISOTROPY_THRESHOLD = 1.0
_NORMAL_GRADIENT_EPS = 1e-12
_STABILIZATION_CONFIDENCE = 0.78
_ADVANCE_RECESSION_CONFIDENCE = 0.70
_RUPTURE_CONFIDENCE = 0.62
_DIAGNOSTIC_CONFIDENCE_CAP = 0.25


@dataclass(frozen=True)
class BoundaryMotionObservation:
    """Checkpoint-local boundary/frontier candidate."""

    checkpoint_id: str
    step_index: int
    node_id: int
    boundary_kind: str
    status: str
    gradient_norm: float | None
    tensor_anisotropy: float | None
    occupied_port_count: int | None
    free_port_count: int | None
    pressure_boundary_provenance: bool
    incident_bridge_edge_ids: tuple[int, ...]
    evidence_fields: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "checkpoint_id": self.checkpoint_id,
                "step_index": self.step_index,
                "node_id": self.node_id,
                "boundary_kind": self.boundary_kind,
                "status": self.status,
                "gradient_norm": self.gradient_norm,
                "tensor_anisotropy": self.tensor_anisotropy,
                "occupied_port_count": self.occupied_port_count,
                "free_port_count": self.free_port_count,
                "pressure_boundary_provenance": self.pressure_boundary_provenance,
                "incident_bridge_edge_ids": list(self.incident_bridge_edge_ids),
                "evidence_fields": list(self.evidence_fields),
            }
        )


@dataclass(frozen=True)
class BoundaryMotionDelta:
    """Boundary/frontier change between adjacent checkpoints."""

    from_checkpoint_id: str
    to_checkpoint_id: str
    from_step: int
    to_step: int
    node_id: int
    motion_event: str
    relationship: str
    boundary_kind: str
    old_observation: BoundaryMotionObservation | None
    new_observation: BoundaryMotionObservation | None
    normal_velocity: float | None
    normal_velocity_status: str
    degradation_reasons: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "from_checkpoint_id": self.from_checkpoint_id,
                "to_checkpoint_id": self.to_checkpoint_id,
                "from_step": self.from_step,
                "to_step": self.to_step,
                "node_id": self.node_id,
                "motion_event": self.motion_event,
                "relationship": self.relationship,
                "boundary_kind": self.boundary_kind,
                "old_observation": None
                if self.old_observation is None
                else self.old_observation.to_mapping(),
                "new_observation": None
                if self.new_observation is None
                else self.new_observation.to_mapping(),
                "normal_velocity": self.normal_velocity,
                "normal_velocity_status": self.normal_velocity_status,
                "degradation_reasons": list(self.degradation_reasons),
            }
        )


@dataclass(frozen=True)
class BoundaryMotionInferenceResult:
    """Boundary/frontier motion records plus diagnostic deltas."""

    window_load_result: MotionWindowLoadResult
    records: tuple[MotionRecord, ...]
    observations: tuple[BoundaryMotionObservation, ...]
    deltas: tuple[BoundaryMotionDelta, ...]
    diagnostic_only: bool

    def to_report(
        self,
        *,
        source_session_id: str | None = None,
        source_artifact_paths: Sequence[str] = (),
    ) -> MotionReport:
        return MotionReport(
            source_session_id=source_session_id
            or _source_session_id_from_path(self.window_load_result.artifact_root),
            source_runtime_family=self.window_load_result.landscape_load_result.source_runtime_family,
            source_artifact_paths=tuple(source_artifact_paths),
            motion_window=self.window_load_result.motion_window,
            records=self.records,
        )

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "classifier_id": BOUNDARY_MOTION_CLASSIFIER_ID,
                "classifier_version": BOUNDARY_MOTION_CLASSIFIER_VERSION,
                "source_runtime_family": (
                    self.window_load_result.landscape_load_result.source_runtime_family
                ),
                "record_count": len(self.records),
                "observation_count": len(self.observations),
                "delta_count": len(self.deltas),
                "diagnostic_only": self.diagnostic_only,
                "motion_window": self.window_load_result.motion_window.to_mapping(),
                "records": [record.to_mapping() for record in self.records],
                "observations": [observation.to_mapping() for observation in self.observations],
                "deltas": [delta.to_mapping() for delta in self.deltas],
            }
        )


def infer_boundary_motion(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    allow_short_persistence_window: bool = True,
) -> BoundaryMotionInferenceResult:
    """Infer boundary/ridge/frontier motion across checkpoint windows."""

    load_result = (
        path_or_result
        if isinstance(path_or_result, MotionWindowLoadResult)
        else load_motion_window(
            path_or_result,
            allow_short_persistence_window=allow_short_persistence_window,
        )
    )
    observations_by_checkpoint = {
        graph.checkpoint_id: _observations_for_graph(graph)
        for graph in load_result.evidence_substrate.checkpoint_graphs
    }
    deltas: list[BoundaryMotionDelta] = []
    records: list[MotionRecord] = []
    graphs = tuple(
        sorted(load_result.evidence_substrate.checkpoint_graphs, key=lambda graph: graph.step_index)
    )
    for previous, current in zip(graphs, graphs[1:]):
        pair_deltas = _deltas_for_graph_pair(
            previous,
            current,
            observations_by_checkpoint.get(previous.checkpoint_id, ()),
            observations_by_checkpoint.get(current.checkpoint_id, ()),
        )
        deltas.extend(pair_deltas)
        records.extend(_record_for_delta(load_result, delta) for delta in pair_deltas)
    return BoundaryMotionInferenceResult(
        window_load_result=load_result,
        records=tuple(records),
        observations=tuple(
            observation
            for graph in graphs
            for observation in observations_by_checkpoint.get(graph.checkpoint_id, ())
        ),
        deltas=tuple(deltas),
        diagnostic_only=load_result.availability.diagnostic_only,
    )


def infer_boundary_motion_report(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    source_session_id: str | None = None,
    source_artifact_paths: Sequence[str] = (),
    **kwargs: Any,
) -> MotionReport:
    """Infer boundary motion and return a serializable motion report."""

    result = infer_boundary_motion(path_or_result, **kwargs)
    return result.to_report(
        source_session_id=source_session_id,
        source_artifact_paths=source_artifact_paths,
    )


def _observations_for_graph(
    graph: LandscapeInferenceCheckpointGraph,
) -> tuple[BoundaryMotionObservation, ...]:
    observations: list[BoundaryMotionObservation] = []
    for node_id, node in sorted(graph.nodes.items()):
        observation = _observation_for_node(graph, node_id, node)
        if observation is not None:
            observations.append(observation)
    return tuple(observations)


def _observation_for_node(
    graph: LandscapeInferenceCheckpointGraph,
    node_id: int,
    node: LandscapeInferenceNodeEvidence,
) -> BoundaryMotionObservation | None:
    gradient_pass = (
        node.gradient_norm is not None
        and node.gradient_norm >= _RIDGE_GRADIENT_THRESHOLD
    )
    tensor_pass = (
        node.tensor_anisotropy is not None
        and node.tensor_anisotropy >= _RIDGE_TENSOR_ANISOTROPY_THRESHOLD
    )
    occupied, free = _port_counts(node)
    port_frontier = occupied is not None and free is not None and occupied > 0 and free > 0
    pressure = _pressure_boundary_label_present(node)
    if gradient_pass or tensor_pass:
        boundary_kind = "geometric_ridge"
        status = "accepted"
    elif port_frontier:
        boundary_kind = "port_frontier"
        status = "accepted"
    elif pressure:
        return None
    else:
        return None
    return BoundaryMotionObservation(
        checkpoint_id=graph.checkpoint_id,
        step_index=graph.step_index,
        node_id=node_id,
        boundary_kind=boundary_kind,
        status=status,
        gradient_norm=node.gradient_norm,
        tensor_anisotropy=node.tensor_anisotropy,
        occupied_port_count=occupied,
        free_port_count=free,
        pressure_boundary_provenance=pressure,
        incident_bridge_edge_ids=_incident_bridge_edge_ids(graph, node_id),
        evidence_fields=_evidence_fields(
            node,
            boundary_kind=boundary_kind,
            pressure_boundary_provenance=pressure,
        ),
    )


def _deltas_for_graph_pair(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    previous_observations: Sequence[BoundaryMotionObservation],
    current_observations: Sequence[BoundaryMotionObservation],
) -> tuple[BoundaryMotionDelta, ...]:
    previous_by_node = {observation.node_id: observation for observation in previous_observations}
    current_by_node = {observation.node_id: observation for observation in current_observations}
    deltas: list[BoundaryMotionDelta] = []
    for node_id in sorted(set(previous_by_node) | set(current_by_node)):
        old = previous_by_node.get(node_id)
        new = current_by_node.get(node_id)
        motion_event, relationship = _motion_event(previous, current, node_id, old, new)
        if motion_event is None:
            continue
        normal_velocity, normal_status = _normal_velocity(previous, current, node_id, old, new)
        reasons = _degradation_reasons(previous, current, node_id, old, new, normal_status)
        deltas.append(
            BoundaryMotionDelta(
                from_checkpoint_id=previous.checkpoint_id,
                to_checkpoint_id=current.checkpoint_id,
                from_step=previous.step_index,
                to_step=current.step_index,
                node_id=node_id,
                motion_event=motion_event,
                relationship=relationship,
                boundary_kind=_boundary_kind(old, new),
                old_observation=old,
                new_observation=new,
                normal_velocity=normal_velocity,
                normal_velocity_status=normal_status,
                degradation_reasons=reasons,
            )
        )
    return tuple(deltas)


def _motion_event(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    node_id: int,
    old: BoundaryMotionObservation | None,
    new: BoundaryMotionObservation | None,
) -> tuple[str | None, str]:
    if old is None and new is not None:
        return ("boundary_advance", "emerged")
    if old is not None and new is None:
        if node_id not in current.nodes:
            return ("boundary_rupture", "dissolved")
        return ("boundary_recession", "dissolved")
    if old is None or new is None:
        return (None, "ambiguous")
    if _free_ports(new) < _free_ports(old):
        return ("frontier_advance", "drifted")
    if _free_ports(new) > _free_ports(old):
        return ("frontier_recession", "drifted")
    if _basin_membership_changed(previous, current, node_id):
        return ("boundary_membership_shift", "drifted")
    ridge_motion = _geometric_ridge_motion(previous, current, node_id, old, new)
    if ridge_motion is not None:
        return (ridge_motion, "drifted")
    if node_id not in previous.nodes:
        return ("boundary_advance", "emerged")
    return ("boundary_stabilization", "stationary")


def _record_for_delta(
    load_result: MotionWindowLoadResult,
    delta: BoundaryMotionDelta,
) -> MotionRecord:
    confidence = _confidence(load_result, delta)
    evidence_quality = _evidence_quality(load_result, delta, confidence=confidence)
    old_node_ids = () if delta.old_observation is None else (delta.node_id,)
    new_node_ids = () if delta.new_observation is None else (delta.node_id,)
    edge_ids = tuple(
        sorted(
            set(
                (delta.old_observation.incident_bridge_edge_ids if delta.old_observation else ())
                + (delta.new_observation.incident_bridge_edge_ids if delta.new_observation else ())
            )
        )
    )
    return MotionRecord(
        motion_id=(
            f"motion_boundary_step{delta.from_step:04d}_{delta.to_step:04d}_"
            f"{delta.motion_event}_node_{delta.node_id}"
        ),
        classifier_id=BOUNDARY_MOTION_CLASSIFIER_ID,
        classifier_version=BOUNDARY_MOTION_CLASSIFIER_VERSION,
        motion_kind="boundary",
        relationship=delta.relationship,
        confidence=confidence,
        evidence_quality=evidence_quality,
        source_runtime_family=load_result.landscape_load_result.source_runtime_family,
        step_window=(delta.from_step, delta.to_step),
        step_ids=(delta.from_step, delta.to_step),
        old_carriers=MotionCarrierSet(
            node_ids=old_node_ids,
            edge_ids=edge_ids,
            primitive_ids=() if old_node_ids or edge_ids else ("no_prior_boundary",),
        ),
        new_carriers=MotionCarrierSet(
            node_ids=new_node_ids,
            edge_ids=edge_ids,
            primitive_ids=() if new_node_ids or edge_ids else ("no_successor_boundary",),
        ),
        evidence=MotionEvidence(
            telemetry_fields=tuple(
                sorted(
                    {
                        "motion_boundary.motion_event",
                        "motion_boundary.normal_velocity",
                        *(delta.old_observation.evidence_fields if delta.old_observation else ()),
                        *(delta.new_observation.evidence_fields if delta.new_observation else ()),
                    }
                )
            ),
            checkpoint_ids=(delta.from_checkpoint_id, delta.to_checkpoint_id),
            step_ids=(delta.from_step, delta.to_step),
            node_ids=(delta.node_id,),
            edge_ids=edge_ids,
            budget_accountability="unavailable",
            degradation_reasons=delta.degradation_reasons,
        ),
        non_claims=(
            "no_identity_motion_claim",
            "not_authored_vs_observed_comparison",
            "pressure_boundary_provenance_not_geometric_ridge",
        ),
    )


def _confidence(load_result: MotionWindowLoadResult, delta: BoundaryMotionDelta) -> float:
    if load_result.availability.diagnostic_only:
        return _DIAGNOSTIC_CONFIDENCE_CAP
    if delta.motion_event == "boundary_stabilization":
        confidence = _STABILIZATION_CONFIDENCE
    elif delta.motion_event == "boundary_rupture":
        confidence = _RUPTURE_CONFIDENCE
    else:
        confidence = _ADVANCE_RECESSION_CONFIDENCE
    if "normal_velocity_unavailable" in delta.degradation_reasons:
        confidence = min(confidence, 0.65)
    if "incident_bridge_edge_flagged" in delta.degradation_reasons:
        confidence = min(confidence, 0.60)
    return confidence


def _evidence_quality(
    load_result: MotionWindowLoadResult,
    delta: BoundaryMotionDelta,
    *,
    confidence: float,
) -> str:
    if load_result.availability.diagnostic_only:
        return "diagnostic_only"
    if delta.motion_event == "boundary_stabilization" and confidence >= 0.75:
        return "strong"
    if confidence >= 0.50:
        return "partial"
    return "degraded"


def _normal_velocity(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    node_id: int,
    old: BoundaryMotionObservation | None,
    new: BoundaryMotionObservation | None,
) -> tuple[float | None, str]:
    if node_id not in previous.nodes or node_id not in current.nodes:
        return (None, "topology_changed")
    old_node = previous.nodes[node_id]
    new_node = current.nodes[node_id]
    if old_node.coherence is None or new_node.coherence is None:
        return (None, "coherence_unavailable")
    gradient = (
        new.gradient_norm
        if new is not None and new.gradient_norm is not None
        else (old.gradient_norm if old is not None else None)
    )
    if gradient is None or abs(float(gradient)) <= _NORMAL_GRADIENT_EPS:
        return (None, "gradient_unavailable")
    delta = _time_delta(previous, current)
    if delta is None or delta <= 0.0:
        return (None, "time_delta_unavailable")
    delta_c = float(new_node.coherence - old_node.coherence)
    return (-delta_c / float(delta) / float(gradient), "available")


def _degradation_reasons(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    node_id: int,
    old: BoundaryMotionObservation | None,
    new: BoundaryMotionObservation | None,
    normal_status: str,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if normal_status != "available":
        reasons.append("normal_velocity_unavailable")
        reasons.append(f"normal_velocity_{normal_status}")
    bridge_ids = set()
    if old is not None:
        bridge_ids.update(old.incident_bridge_edge_ids)
    if new is not None:
        bridge_ids.update(new.incident_bridge_edge_ids)
    if bridge_ids:
        reasons.append("incident_bridge_edge_flagged")
    pressure = bool(
        (old is not None and old.pressure_boundary_provenance)
        or (new is not None and new.pressure_boundary_provenance)
    )
    if pressure:
        reasons.append("pressure_boundary_provenance_separate")
    if _basin_membership_changed(previous, current, node_id):
        reasons.append("basin_membership_changed")
    if node_id not in previous.nodes or node_id not in current.nodes:
        reasons.append("topology_delta_boundary")
    return tuple(sorted(set(reasons)))


def _basin_membership_changed(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    node_id: int,
) -> bool:
    if node_id not in previous.nodes or node_id not in current.nodes:
        return False
    old_basin_id = previous.nodes[node_id].basin_id
    new_basin_id = current.nodes[node_id].basin_id
    return old_basin_id is not None and new_basin_id is not None and old_basin_id != new_basin_id


def _geometric_ridge_motion(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
    node_id: int,
    old: BoundaryMotionObservation | None,
    new: BoundaryMotionObservation | None,
) -> str | None:
    if old is None or new is None:
        return None
    if old.boundary_kind != "geometric_ridge" or new.boundary_kind != "geometric_ridge":
        return None
    normal_velocity, normal_status = _normal_velocity(previous, current, node_id, old, new)
    if normal_status != "available" or normal_velocity is None:
        return None
    if normal_velocity > _NORMAL_GRADIENT_EPS:
        return "boundary_advance"
    if normal_velocity < -_NORMAL_GRADIENT_EPS:
        return "boundary_recession"
    return None


def _time_delta(
    previous: LandscapeInferenceCheckpointGraph,
    current: LandscapeInferenceCheckpointGraph,
) -> float | None:
    if previous.time is not None and current.time is not None:
        return float(current.time - previous.time)
    return float(current.step_index - previous.step_index)


def _port_counts(node: LandscapeInferenceNodeEvidence) -> tuple[int | None, int | None]:
    if node.port_matrix is None:
        return (None, None)
    occupied = sum(1 for row in node.port_matrix for item in row if item)
    return (occupied, 9 - occupied)


def _free_ports(observation: BoundaryMotionObservation) -> int:
    return int(observation.free_port_count or 0)


def _incident_bridge_edge_ids(
    graph: LandscapeInferenceCheckpointGraph,
    node_id: int,
) -> tuple[int, ...]:
    edge_ids: list[int] = []
    for edge_id, edge in graph.edges.items():
        if not edge.is_bridge:
            continue
        if edge.source_node_id == node_id or edge.target_node_id == node_id:
            edge_ids.append(edge_id)
    return tuple(sorted(edge_ids))


def _pressure_boundary_label_present(node: LandscapeInferenceNodeEvidence) -> bool:
    for mapping in (node.payload, node.provenance):
        for value in mapping.values():
            text = str(value)
            if "pressure_boundary" in text or "front_capacity" in text:
                return True
    return False


def _evidence_fields(
    node: LandscapeInferenceNodeEvidence,
    *,
    boundary_kind: str,
    pressure_boundary_provenance: bool,
) -> tuple[str, ...]:
    fields: list[str] = ["graph_checkpoints.node_records.node_id"]
    if node.gradient_norm is not None:
        fields.append("graph_checkpoints.node_records.gradient_norm")
    if node.tensor_anisotropy is not None:
        fields.append("graph_checkpoints.node_records.tensor_anisotropy")
    if node.port_matrix is not None:
        fields.append("graph_checkpoints.node_records.port_matrix")
    if boundary_kind == "port_frontier":
        fields.append("motion_boundary.port_frontier")
    if pressure_boundary_provenance:
        fields.append("graph_checkpoints.node_records.pressure_boundary_provenance")
    return tuple(fields)


def _boundary_kind(
    old: BoundaryMotionObservation | None,
    new: BoundaryMotionObservation | None,
) -> str:
    if new is not None:
        return new.boundary_kind
    if old is not None:
        return old.boundary_kind
    return "unknown_boundary"


def _source_session_id_from_path(path: Path) -> str:
    return path.name or "unknown_session"


__all__ = [
    "BOUNDARY_MOTION_CLASSIFIER_ID",
    "BOUNDARY_MOTION_CLASSIFIER_VERSION",
    "BoundaryMotionDelta",
    "BoundaryMotionInferenceResult",
    "BoundaryMotionObservation",
    "infer_boundary_motion",
    "infer_boundary_motion_report",
]
