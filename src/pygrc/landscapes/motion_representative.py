"""Representative-motion observer over normalized motion windows."""

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
from .motion_loader import (
    MotionCheckpointEvidence,
    MotionCheckpointNodeEvidence,
    MotionWindowLoadResult,
    load_motion_window,
)


REPRESENTATIVE_MOTION_CLASSIFIER_ID = "motion_representative_observer"
REPRESENTATIVE_MOTION_CLASSIFIER_VERSION = "motion_inference_iter4_v1"

_STABLE_CONFIDENCE = 0.80
_DRIFT_CONFIDENCE = 0.70
_AMBIGUOUS_CONFIDENCE = 0.55
_DIAGNOSTIC_CONFIDENCE_CAP = 0.25


@dataclass(frozen=True)
class RepresentativeMotionSelection:
    """One checkpoint-local representative selection for a basin/group."""

    checkpoint_id: str
    step_index: int
    group_id: str
    representative_node_id: int
    selection_mode: str
    member_node_ids: tuple[int, ...]
    coordinates: tuple[float, ...] | None
    candidate_modes: tuple[str, ...]
    evidence_quality: str

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "checkpoint_id": self.checkpoint_id,
                "step_index": self.step_index,
                "group_id": self.group_id,
                "representative_node_id": self.representative_node_id,
                "selection_mode": self.selection_mode,
                "member_node_ids": list(self.member_node_ids),
                "coordinates": None if self.coordinates is None else list(self.coordinates),
                "candidate_modes": list(self.candidate_modes),
                "evidence_quality": self.evidence_quality,
            }
        )


@dataclass(frozen=True)
class RepresentativeMotionInferenceResult:
    """Representative-motion records plus selection diagnostics."""

    window_load_result: MotionWindowLoadResult
    records: tuple[MotionRecord, ...]
    selections: tuple[RepresentativeMotionSelection, ...]
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
                "classifier_id": REPRESENTATIVE_MOTION_CLASSIFIER_ID,
                "classifier_version": REPRESENTATIVE_MOTION_CLASSIFIER_VERSION,
                "source_runtime_family": (
                    self.window_load_result.landscape_load_result.source_runtime_family
                ),
                "record_count": len(self.records),
                "selection_count": len(self.selections),
                "diagnostic_only": self.diagnostic_only,
                "motion_window": self.window_load_result.motion_window.to_mapping(),
                "records": [record.to_mapping() for record in self.records],
                "selections": [selection.to_mapping() for selection in self.selections],
            }
        )


def infer_representative_motion(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    allow_short_persistence_window: bool = True,
) -> RepresentativeMotionInferenceResult:
    """Infer representative stability/change across checkpoint windows."""

    load_result = (
        path_or_result
        if isinstance(path_or_result, MotionWindowLoadResult)
        else load_motion_window(
            path_or_result,
            allow_short_persistence_window=allow_short_persistence_window,
        )
    )
    selections_by_checkpoint = {
        checkpoint.checkpoint_id: _selections_for_checkpoint(checkpoint)
        for checkpoint in load_result.checkpoint_evidence
    }
    records: list[MotionRecord] = []
    for previous, current in zip(
        load_result.checkpoint_evidence,
        load_result.checkpoint_evidence[1:],
    ):
        records.extend(
            _records_for_checkpoint_pair(
                load_result,
                previous,
                current,
                selections_by_checkpoint.get(previous.checkpoint_id, ()),
                selections_by_checkpoint.get(current.checkpoint_id, ()),
            )
        )
    return RepresentativeMotionInferenceResult(
        window_load_result=load_result,
        records=tuple(records),
        selections=tuple(
            selection
            for checkpoint in load_result.checkpoint_evidence
            for selection in selections_by_checkpoint.get(checkpoint.checkpoint_id, ())
        ),
        diagnostic_only=load_result.availability.diagnostic_only,
    )


def infer_representative_motion_report(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    source_session_id: str | None = None,
    source_artifact_paths: Sequence[str] = (),
    **kwargs: Any,
) -> MotionReport:
    """Infer representative motion and return a serializable motion report."""

    result = infer_representative_motion(path_or_result, **kwargs)
    return result.to_report(
        source_session_id=source_session_id,
        source_artifact_paths=source_artifact_paths,
    )


def select_representatives_for_checkpoint(
    checkpoint: MotionCheckpointEvidence,
) -> tuple[RepresentativeMotionSelection, ...]:
    """Select deterministic representatives for one normalized checkpoint."""

    return _selections_for_checkpoint(checkpoint)


def _selections_for_checkpoint(
    checkpoint: MotionCheckpointEvidence,
) -> tuple[RepresentativeMotionSelection, ...]:
    selections: list[RepresentativeMotionSelection] = []
    for group_id, member_node_ids in _node_groups(checkpoint.nodes).items():
        selection = _select_representative(checkpoint, group_id, member_node_ids)
        if selection is not None:
            selections.append(selection)
    return tuple(sorted(selections, key=lambda item: item.group_id))


def _node_groups(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
) -> dict[str, tuple[int, ...]]:
    grouped: dict[str, list[int]] = {}
    for node_id, node in sorted(nodes.items()):
        group_id = node.basin_id if node.basin_id is not None else f"node_{node_id}"
        grouped.setdefault(group_id, []).append(node_id)
    return {key: tuple(value) for key, value in sorted(grouped.items())}


def _select_representative(
    checkpoint: MotionCheckpointEvidence,
    group_id: str,
    member_node_ids: Sequence[int],
) -> RepresentativeMotionSelection | None:
    members = tuple(sorted(int(node_id) for node_id in member_node_ids))
    if not members:
        return None
    sink = _first_mode_node(checkpoint.nodes, members, "sink")
    if sink is not None:
        return _selection(checkpoint, group_id, members, sink, "sink")
    centroid = _centroid_nearest_node(checkpoint.nodes, members)
    if centroid is not None:
        return _selection(checkpoint, group_id, members, centroid, "centroid_nearest_node")
    peak = _peak_coherence_node(checkpoint.nodes, members)
    if peak is not None:
        return _selection(checkpoint, group_id, members, peak, "peak_coherence")
    front = _first_mode_node(checkpoint.nodes, members, "port_front_candidate")
    if front is not None:
        return _selection(checkpoint, group_id, members, front, "port_front_candidate")
    medoid = _graph_medoid_proxy(checkpoint, members)
    if medoid is not None:
        return _selection(checkpoint, group_id, members, medoid, "graph_medoid_proxy")
    return _selection(checkpoint, group_id, members, members[0], "lowest_node_id_fallback")


def _selection(
    checkpoint: MotionCheckpointEvidence,
    group_id: str,
    member_node_ids: tuple[int, ...],
    representative_node_id: int,
    selection_mode: str,
) -> RepresentativeMotionSelection:
    node = checkpoint.nodes[representative_node_id]
    candidate_modes = tuple(
        sorted(
            set(node.representative_modes)
            | ({selection_mode} if selection_mode else set())
        )
    )
    return RepresentativeMotionSelection(
        checkpoint_id=checkpoint.checkpoint_id,
        step_index=checkpoint.step_index,
        group_id=group_id,
        representative_node_id=representative_node_id,
        selection_mode=selection_mode,
        member_node_ids=member_node_ids,
        coordinates=node.coordinates,
        candidate_modes=candidate_modes,
        evidence_quality=_selection_quality(selection_mode),
    )


def _selection_quality(selection_mode: str) -> str:
    if selection_mode in {"sink", "peak_coherence", "centroid_nearest_node"}:
        return "strong"
    if selection_mode in {"graph_medoid_proxy", "port_front_candidate"}:
        return "partial"
    return "degraded"


def _records_for_checkpoint_pair(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    previous_selections: Sequence[RepresentativeMotionSelection],
    current_selections: Sequence[RepresentativeMotionSelection],
) -> tuple[MotionRecord, ...]:
    previous_by_group = {selection.group_id: selection for selection in previous_selections}
    current_by_group = {selection.group_id: selection for selection in current_selections}
    records: list[MotionRecord] = []
    for group_id in sorted(set(previous_by_group) & set(current_by_group)):
        old = previous_by_group[group_id]
        new = current_by_group[group_id]
        records.append(_motion_record(load_result, previous, current, old, new))
    return tuple(records)


def _motion_record(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    old: RepresentativeMotionSelection,
    new: RepresentativeMotionSelection,
) -> MotionRecord:
    same_node = old.representative_node_id == new.representative_node_id
    relationship = "stationary" if same_node else "drifted"
    confidence = _record_confidence(load_result, old, new, same_node=same_node)
    evidence_quality = _record_quality(load_result, old, new, confidence=confidence)
    degradation_reasons = _degradation_reasons(load_result, old, new)
    step_ids = (previous.step_index, current.step_index)
    node_ids = tuple(sorted({old.representative_node_id, new.representative_node_id}))
    return MotionRecord(
        motion_id=(
            f"motion_representative_step{previous.step_index:04d}_"
            f"{current.step_index:04d}_{_safe_id(old.group_id)}"
        ),
        classifier_id=REPRESENTATIVE_MOTION_CLASSIFIER_ID,
        classifier_version=REPRESENTATIVE_MOTION_CLASSIFIER_VERSION,
        motion_kind="representative",
        relationship=relationship,
        confidence=confidence,
        evidence_quality=evidence_quality,
        source_runtime_family=load_result.landscape_load_result.source_runtime_family,
        step_window=(previous.step_index, current.step_index),
        step_ids=step_ids,
        old_carriers=MotionCarrierSet(
            node_ids=(old.representative_node_id,),
            basin_ids=(old.group_id,),
        ),
        new_carriers=MotionCarrierSet(
            node_ids=(new.representative_node_id,),
            basin_ids=(new.group_id,),
        ),
        evidence=MotionEvidence(
            telemetry_fields=(
                "checkpoint.node_records.coherence",
                "checkpoint.node_records.basin_id",
                "checkpoint.node_records.is_sink",
                "checkpoint.node_records.payload.coordinates",
                f"motion_representative.selection_mode.{old.selection_mode}",
                f"motion_representative.selection_mode.{new.selection_mode}",
            ),
            checkpoint_ids=(previous.checkpoint_id, current.checkpoint_id),
            step_ids=step_ids,
            node_ids=node_ids,
            budget_accountability="unavailable",
            degradation_reasons=degradation_reasons,
        ),
        non_claims=(
            "no_identity_motion_claim",
            "representative_change_not_identity_walking",
        ),
    )


def _record_confidence(
    load_result: MotionWindowLoadResult,
    old: RepresentativeMotionSelection,
    new: RepresentativeMotionSelection,
    *,
    same_node: bool,
) -> float:
    confidence = _STABLE_CONFIDENCE if same_node else _DRIFT_CONFIDENCE
    if old.evidence_quality == "degraded" or new.evidence_quality == "degraded":
        confidence = min(confidence, _AMBIGUOUS_CONFIDENCE)
    elif old.evidence_quality == "partial" or new.evidence_quality == "partial":
        confidence = min(confidence, 0.65)
    if load_result.availability.diagnostic_only:
        confidence = min(confidence, _DIAGNOSTIC_CONFIDENCE_CAP)
    return confidence


def _record_quality(
    load_result: MotionWindowLoadResult,
    old: RepresentativeMotionSelection,
    new: RepresentativeMotionSelection,
    *,
    confidence: float,
) -> str:
    if load_result.availability.diagnostic_only:
        return "diagnostic_only"
    if old.evidence_quality == "degraded" or new.evidence_quality == "degraded":
        return "degraded"
    if old.evidence_quality == "partial" or new.evidence_quality == "partial" or confidence < 0.80:
        return "partial"
    return "strong"


def _degradation_reasons(
    load_result: MotionWindowLoadResult,
    old: RepresentativeMotionSelection,
    new: RepresentativeMotionSelection,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if load_result.availability.diagnostic_only:
        reasons.append("diagnostic_only_window")
    if old.selection_mode != new.selection_mode:
        reasons.append("selection_mode_changed")
    for selection in (old, new):
        if selection.selection_mode == "graph_medoid_proxy":
            reasons.append("coordinate_surface_unavailable")
        elif selection.selection_mode == "lowest_node_id_fallback":
            reasons.append("representative_surface_degraded")
    return tuple(sorted(set(reasons)))


def _first_mode_node(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    member_node_ids: Sequence[int],
    mode: str,
) -> int | None:
    for node_id in sorted(member_node_ids):
        if mode in nodes[node_id].representative_modes:
            return int(node_id)
    return None


def _peak_coherence_node(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    member_node_ids: Sequence[int],
) -> int | None:
    candidates = [
        (float(nodes[node_id].coherence), int(node_id))
        for node_id in member_node_ids
        if nodes[node_id].coherence is not None
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], -item[1]))[1]


def _centroid_nearest_node(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    member_node_ids: Sequence[int],
) -> int | None:
    centroid = _weighted_centroid(member_node_ids, nodes)
    if centroid is None:
        return None
    candidates: list[tuple[float, int]] = []
    for node_id in member_node_ids:
        coordinates = nodes[node_id].coordinates
        if coordinates is None:
            continue
        distance = _distance(centroid, coordinates)
        candidates.append((distance, int(node_id)))
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item[0], item[1]))[1]


def _weighted_centroid(
    member_node_ids: Sequence[int],
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
) -> tuple[float, ...] | None:
    weighted_sum: list[float] | None = None
    total_weight = 0.0
    for node_id in member_node_ids:
        node = nodes[node_id]
        if node.coordinates is None:
            continue
        weight = 1.0 if node.coherence is None else max(float(node.coherence), 0.0)
        if weighted_sum is None:
            weighted_sum = [0.0 for _ in node.coordinates]
        dimension = min(len(weighted_sum), len(node.coordinates))
        for index in range(dimension):
            weighted_sum[index] += float(node.coordinates[index]) * weight
        total_weight += weight
    if weighted_sum is None or total_weight <= 0.0:
        return None
    return tuple(value / total_weight for value in weighted_sum)


def _graph_medoid_proxy(
    checkpoint: MotionCheckpointEvidence,
    member_node_ids: Sequence[int],
) -> int | None:
    members = tuple(sorted(int(node_id) for node_id in member_node_ids))
    if not members:
        return None
    adjacency = _adjacency(checkpoint)
    distances: list[tuple[int, int]] = []
    for node_id in members:
        distances.append((_distance_sum(node_id, members, adjacency), node_id))
    return min(distances, key=lambda item: (item[0], item[1]))[1]


def _adjacency(checkpoint: MotionCheckpointEvidence) -> dict[int, tuple[int, ...]]:
    adjacency: dict[int, set[int]] = {node_id: set() for node_id in checkpoint.nodes}
    for edge in checkpoint.edges.values():
        adjacency.setdefault(edge.source_node_id, set()).add(edge.target_node_id)
        adjacency.setdefault(edge.target_node_id, set()).add(edge.source_node_id)
    return {node_id: tuple(sorted(neighbors)) for node_id, neighbors in adjacency.items()}


def _distance_sum(
    start_node_id: int,
    member_node_ids: Sequence[int],
    adjacency: Mapping[int, Sequence[int]],
) -> int:
    distances = _shortest_distances(start_node_id, adjacency)
    missing_penalty = len(member_node_ids) + len(adjacency) + 1
    return sum(int(distances.get(node_id, missing_penalty)) for node_id in member_node_ids)


def _shortest_distances(
    start_node_id: int,
    adjacency: Mapping[int, Sequence[int]],
) -> dict[int, int]:
    distances = {start_node_id: 0}
    queue = [start_node_id]
    for node_id in queue:
        for neighbor in adjacency.get(node_id, ()):
            if neighbor in distances:
                continue
            distances[neighbor] = distances[node_id] + 1
            queue.append(neighbor)
    return distances


def _distance(first: Sequence[float], second: Sequence[float]) -> float:
    dimension = min(len(first), len(second))
    return math.sqrt(
        sum((float(first[index]) - float(second[index])) ** 2 for index in range(dimension))
    )


def _safe_id(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_") or "group"


def _source_session_id_from_path(path: Path) -> str:
    return path.name or "unknown_session"


__all__ = [
    "REPRESENTATIVE_MOTION_CLASSIFIER_ID",
    "REPRESENTATIVE_MOTION_CLASSIFIER_VERSION",
    "RepresentativeMotionInferenceResult",
    "RepresentativeMotionSelection",
    "infer_representative_motion",
    "infer_representative_motion_report",
    "select_representatives_for_checkpoint",
]
