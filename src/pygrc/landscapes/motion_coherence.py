"""Coherence-motion observer over normalized motion windows."""

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
    MotionCheckpointEdgeEvidence,
    MotionCheckpointEvidence,
    MotionCheckpointNodeEvidence,
    MotionWindowLoadResult,
    load_motion_window,
)


COHERENCE_MOTION_CLASSIFIER_ID = "motion_coherence_observer"
COHERENCE_MOTION_CLASSIFIER_VERSION = "motion_inference_iter3_v1"

_DEFAULT_MIN_COHERENCE_DELTA = 1e-9
_DEFAULT_MIN_FLUX_SUPPORT = 1e-12
_DEFAULT_BUDGET_LEAK_THRESHOLD = 1e-9
_DEFAULT_CONTINUITY_TOLERANCE = 1e-6


@dataclass(frozen=True)
class CoherenceMotionDriftEstimate:
    """Graph-local basin drift estimate from coherence-weighted coordinates."""

    basin_id: str
    from_checkpoint_id: str
    to_checkpoint_id: str
    from_step: int
    to_step: int
    support_node_ids: tuple[int, ...]
    displacement: tuple[float, ...]
    velocity: tuple[float, ...] | None
    speed: float | None
    evidence_quality: str

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "basin_id": self.basin_id,
                "from_checkpoint_id": self.from_checkpoint_id,
                "to_checkpoint_id": self.to_checkpoint_id,
                "from_step": self.from_step,
                "to_step": self.to_step,
                "support_node_ids": list(self.support_node_ids),
                "displacement": list(self.displacement),
                "velocity": None if self.velocity is None else list(self.velocity),
                "speed": self.speed,
                "evidence_quality": self.evidence_quality,
            }
        )


@dataclass(frozen=True)
class CoherenceMotionInferenceResult:
    """Coherence-motion records plus diagnostic observer summaries."""

    window_load_result: MotionWindowLoadResult
    records: tuple[MotionRecord, ...]
    drift_estimates: tuple[CoherenceMotionDriftEstimate, ...]
    quadrature_mode: str
    budget_accountability: str
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
                "classifier_id": COHERENCE_MOTION_CLASSIFIER_ID,
                "classifier_version": COHERENCE_MOTION_CLASSIFIER_VERSION,
                "source_runtime_family": (
                    self.window_load_result.landscape_load_result.source_runtime_family
                ),
                "record_count": len(self.records),
                "drift_estimate_count": len(self.drift_estimates),
                "quadrature_mode": self.quadrature_mode,
                "budget_accountability": self.budget_accountability,
                "diagnostic_only": self.diagnostic_only,
                "motion_window": self.window_load_result.motion_window.to_mapping(),
                "records": [record.to_mapping() for record in self.records],
                "drift_estimates": [
                    estimate.to_mapping() for estimate in self.drift_estimates
                ],
            }
        )


def infer_coherence_motion(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    min_coherence_delta: float = _DEFAULT_MIN_COHERENCE_DELTA,
    min_flux_support: float = _DEFAULT_MIN_FLUX_SUPPORT,
    budget_leak_threshold: float = _DEFAULT_BUDGET_LEAK_THRESHOLD,
    continuity_tolerance: float = _DEFAULT_CONTINUITY_TOLERANCE,
    allow_short_persistence_window: bool = True,
) -> CoherenceMotionInferenceResult:
    """Infer coherence transfer across graph carriers from checkpoint evidence."""

    load_result = (
        path_or_result
        if isinstance(path_or_result, MotionWindowLoadResult)
        else load_motion_window(
            path_or_result,
            allow_short_persistence_window=allow_short_persistence_window,
        )
    )
    if min_coherence_delta < 0.0:
        raise ValueError("min_coherence_delta must be non-negative")
    if min_flux_support < 0.0:
        raise ValueError("min_flux_support must be non-negative")
    if budget_leak_threshold < 0.0:
        raise ValueError("budget_leak_threshold must be non-negative")
    budget_accountability = _budget_accountability(
        load_result,
        budget_leak_threshold=budget_leak_threshold,
    )
    diagnostic_only = load_result.availability.diagnostic_only
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
                min_coherence_delta=min_coherence_delta,
                min_flux_support=min_flux_support,
                continuity_tolerance=continuity_tolerance,
                budget_accountability=budget_accountability,
                diagnostic_only=diagnostic_only,
            )
        )
    return CoherenceMotionInferenceResult(
        window_load_result=load_result,
        records=tuple(records),
        drift_estimates=estimate_basin_drift_velocities(load_result),
        quadrature_mode=load_result.quadrature_mode,
        budget_accountability=budget_accountability,
        diagnostic_only=diagnostic_only,
    )


def infer_coherence_motion_report(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    source_session_id: str | None = None,
    source_artifact_paths: Sequence[str] = (),
    **kwargs: Any,
) -> MotionReport:
    """Infer coherence motion and return a serializable motion report."""

    result = infer_coherence_motion(path_or_result, **kwargs)
    return result.to_report(
        source_session_id=source_session_id,
        source_artifact_paths=source_artifact_paths,
    )


def estimate_basin_drift_velocities(
    load_result: MotionWindowLoadResult,
) -> tuple[CoherenceMotionDriftEstimate, ...]:
    """Estimate basin drift from coherence-weighted checkpoint coordinates."""

    estimates: list[CoherenceMotionDriftEstimate] = []
    for previous, current in zip(
        load_result.checkpoint_evidence,
        load_result.checkpoint_evidence[1:],
    ):
        previous_basins = _nodes_by_basin(previous.nodes)
        current_basins = _nodes_by_basin(current.nodes)
        for basin_id in sorted(set(previous_basins) & set(current_basins)):
            old_centroid = _weighted_centroid(previous_basins[basin_id], previous.nodes)
            new_centroid = _weighted_centroid(current_basins[basin_id], current.nodes)
            if old_centroid is None or new_centroid is None:
                continue
            dimension = min(len(old_centroid), len(new_centroid))
            displacement = tuple(
                float(new_centroid[index] - old_centroid[index])
                for index in range(dimension)
            )
            elapsed = _elapsed_time(previous, current)
            velocity = None if elapsed is None else tuple(value / elapsed for value in displacement)
            speed = None if velocity is None else math.sqrt(sum(value * value for value in velocity))
            estimates.append(
                CoherenceMotionDriftEstimate(
                    basin_id=basin_id,
                    from_checkpoint_id=previous.checkpoint_id,
                    to_checkpoint_id=current.checkpoint_id,
                    from_step=previous.step_index,
                    to_step=current.step_index,
                    support_node_ids=tuple(
                        sorted(set(previous_basins[basin_id]) | set(current_basins[basin_id]))
                    ),
                    displacement=displacement,
                    velocity=velocity,
                    speed=speed,
                    evidence_quality="strong" if elapsed is not None else "partial",
                )
            )
    return tuple(estimates)


def _records_for_checkpoint_pair(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    *,
    min_coherence_delta: float,
    min_flux_support: float,
    continuity_tolerance: float,
    budget_accountability: str,
    diagnostic_only: bool,
) -> tuple[MotionRecord, ...]:
    deltas = _coherence_deltas(previous, current, min_coherence_delta=min_coherence_delta)
    losers = tuple(sorted(node_id for node_id, delta in deltas.items() if delta < 0.0))
    gainers = tuple(sorted(node_id for node_id, delta in deltas.items() if delta > 0.0))
    if not losers or not gainers:
        return ()
    pair_edges = _edge_evidence_by_pair(previous, current)
    records: list[MotionRecord] = []
    for loser in losers:
        for gainer in gainers:
            support = _direct_flux_support(
                pair_edges.get(_pair_key(loser, gainer)),
                from_node_id=loser,
                to_node_id=gainer,
                min_flux_support=min_flux_support,
            )
            if support is None:
                continue
            records.append(
                _motion_record(
                    load_result,
                    previous,
                    current,
                    relationship="drifted",
                    old_node_ids=(loser,),
                    new_node_ids=(gainer,),
                    edge_ids=(support.edge_id,),
                    transferred_mass=min(abs(deltas[loser]), abs(deltas[gainer])),
                    confidence_base=0.85,
                    budget_accountability=budget_accountability,
                    diagnostic_only=diagnostic_only,
                    degradation_reasons=_degradation_reasons(
                        previous,
                        current,
                        deltas,
                        (loser, gainer),
                        budget_accountability=budget_accountability,
                        continuity_tolerance=continuity_tolerance,
                    ),
                    suffix=f"{loser}_to_{gainer}_direct",
                )
            )
    if records:
        return tuple(records)
    supported_edges = tuple(
        edge.edge_id
        for edge in pair_edges.values()
        if edge.signed_flux is not None and abs(edge.signed_flux) > min_flux_support
    )
    if not supported_edges:
        return ()
    records.append(
        _motion_record(
            load_result,
            previous,
            current,
            relationship="ambiguous",
            old_node_ids=losers,
            new_node_ids=gainers,
            edge_ids=tuple(sorted(supported_edges)),
            transferred_mass=min(
                sum(abs(deltas[node_id]) for node_id in losers),
                sum(abs(deltas[node_id]) for node_id in gainers),
            ),
            confidence_base=0.55,
            budget_accountability=budget_accountability,
            diagnostic_only=diagnostic_only,
            degradation_reasons=(
                *_degradation_reasons(
                    previous,
                    current,
                    deltas,
                    (*losers, *gainers),
                    budget_accountability=budget_accountability,
                    continuity_tolerance=continuity_tolerance,
                ),
                "multi_edge_or_indirect_transfer",
            ),
            suffix="ambiguous_multi_edge",
        )
    )
    return tuple(records)


def _motion_record(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    *,
    relationship: str,
    old_node_ids: tuple[int, ...],
    new_node_ids: tuple[int, ...],
    edge_ids: tuple[int, ...],
    transferred_mass: float,
    confidence_base: float,
    budget_accountability: str,
    diagnostic_only: bool,
    degradation_reasons: tuple[str, ...],
    suffix: str,
) -> MotionRecord:
    degraded_reasons = tuple(sorted(set(degradation_reasons)))
    confidence = confidence_base
    evidence_quality = "strong" if relationship == "drifted" else "partial"
    if diagnostic_only:
        confidence = min(confidence, 0.25)
        evidence_quality = "diagnostic_only"
        degraded_reasons = tuple(sorted((*degraded_reasons, "diagnostic_only_window")))
    if "budget_leak" in degraded_reasons:
        confidence = min(confidence, 0.45)
        evidence_quality = "degraded"
    elif degraded_reasons and evidence_quality == "strong":
        confidence = min(confidence, 0.65)
        evidence_quality = "partial"
    step_ids = (previous.step_index, current.step_index)
    node_ids = tuple(sorted(set(old_node_ids) | set(new_node_ids)))
    return MotionRecord(
        motion_id=(
            f"motion_coherence_step{previous.step_index:04d}_"
            f"{current.step_index:04d}_{suffix}"
        ),
        classifier_id=COHERENCE_MOTION_CLASSIFIER_ID,
        classifier_version=COHERENCE_MOTION_CLASSIFIER_VERSION,
        motion_kind="coherence",
        relationship=relationship,
        confidence=confidence,
        evidence_quality=evidence_quality,
        source_runtime_family=load_result.landscape_load_result.source_runtime_family,
        step_window=(previous.step_index, current.step_index),
        step_ids=step_ids,
        old_carriers=MotionCarrierSet(node_ids=old_node_ids),
        new_carriers=MotionCarrierSet(node_ids=new_node_ids),
        evidence=MotionEvidence(
            telemetry_fields=(
                "checkpoint.node_records.coherence",
                "checkpoint.edge_records.signed_flux",
                "checkpoint.node_records.payload.continuity_delta",
                "checkpoint.budget_audit.quadrature_weight_mode",
            ),
            checkpoint_ids=(previous.checkpoint_id, current.checkpoint_id),
            step_ids=step_ids,
            node_ids=node_ids,
            edge_ids=tuple(sorted(edge_ids)),
            budget_accountability=budget_accountability,
            degradation_reasons=degraded_reasons,
        ),
        transferred_mass=float(max(0.0, transferred_mass)),
        non_claims=(
            "no_identity_motion_claim",
            "node_carrier_not_identity",
        ),
    )


def _coherence_deltas(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    *,
    min_coherence_delta: float,
) -> dict[int, float]:
    deltas: dict[int, float] = {}
    for node_id in sorted(set(previous.nodes) & set(current.nodes)):
        old = previous.nodes[node_id].coherence
        new = current.nodes[node_id].coherence
        if old is None or new is None:
            continue
        delta = float(new - old)
        if abs(delta) > min_coherence_delta:
            deltas[node_id] = delta
    return deltas


def _edge_evidence_by_pair(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
) -> dict[tuple[int, int], MotionCheckpointEdgeEvidence]:
    edges: dict[tuple[int, int], MotionCheckpointEdgeEvidence] = {}
    for source in (previous.edges, current.edges):
        for edge in source.values():
            key = _pair_key(edge.source_node_id, edge.target_node_id)
            existing = edges.get(key)
            if existing is None or existing.signed_flux is None:
                edges[key] = edge
    return edges


def _direct_flux_support(
    edge: MotionCheckpointEdgeEvidence | None,
    *,
    from_node_id: int,
    to_node_id: int,
    min_flux_support: float,
) -> MotionCheckpointEdgeEvidence | None:
    if edge is None or edge.signed_flux is None or abs(edge.signed_flux) <= min_flux_support:
        return None
    if edge.source_node_id == from_node_id and edge.target_node_id == to_node_id:
        return edge if edge.signed_flux > min_flux_support else None
    if edge.source_node_id == to_node_id and edge.target_node_id == from_node_id:
        return edge if edge.signed_flux < -min_flux_support else None
    return None


def _degradation_reasons(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    deltas: Mapping[int, float],
    node_ids: Sequence[int],
    *,
    budget_accountability: str,
    continuity_tolerance: float,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if budget_accountability == "leak_error":
        reasons.append("budget_leak")
    for node_id in node_ids:
        observed = deltas.get(node_id)
        if observed is None:
            continue
        continuity = _interval_continuity_delta(previous, current, node_id)
        if continuity is None:
            reasons.append("continuity_delta_unavailable")
            continue
        if abs(float(continuity) - float(observed)) > continuity_tolerance:
            reasons.append("continuity_delta_mismatch")
    return tuple(sorted(set(reasons)))


def _interval_continuity_delta(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    node_id: int,
) -> float | None:
    node = current.nodes.get(node_id)
    if node is not None and node.continuity_delta is not None:
        return node.continuity_delta
    node = previous.nodes.get(node_id)
    if node is not None:
        return node.continuity_delta
    return None


def _budget_accountability(
    load_result: MotionWindowLoadResult,
    *,
    budget_leak_threshold: float,
) -> str:
    modes: set[str] = set()
    for graph in load_result.evidence_substrate.checkpoint_graphs:
        audit = graph.budget_audit
        if audit.budget_error is not None and abs(audit.budget_error) > budget_leak_threshold:
            return "leak_error"
        modes.add(str(audit.budget_accountability))
    if "conserved_zero" in modes and len(modes - {"conserved_zero", "unavailable"}) == 0:
        return "conserved_zero"
    return "unavailable"


def _nodes_by_basin(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
) -> dict[str, tuple[int, ...]]:
    grouped: dict[str, list[int]] = {}
    for node_id, node in sorted(nodes.items()):
        if node.basin_id is None:
            continue
        grouped.setdefault(node.basin_id, []).append(node_id)
    return {key: tuple(value) for key, value in sorted(grouped.items())}


def _weighted_centroid(
    node_ids: Sequence[int],
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
) -> tuple[float, ...] | None:
    weighted_sum: list[float] | None = None
    total_weight = 0.0
    for node_id in node_ids:
        node = nodes[node_id]
        if node.coordinates is None or node.coherence is None:
            continue
        weight = max(float(node.coherence), 0.0)
        if weight == 0.0:
            continue
        if weighted_sum is None:
            weighted_sum = [0.0 for _ in node.coordinates]
        dimension = min(len(weighted_sum), len(node.coordinates))
        for index in range(dimension):
            weighted_sum[index] += float(node.coordinates[index]) * weight
        total_weight += weight
    if weighted_sum is None or total_weight <= 0.0:
        return None
    return tuple(value / total_weight for value in weighted_sum)


def _elapsed_time(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
) -> float | None:
    if previous.time is not None and current.time is not None:
        delta = float(current.time - previous.time)
        if delta > 0.0:
            return delta
    step_delta = int(current.step_index - previous.step_index)
    if step_delta > 0:
        return float(step_delta)
    return None


def _pair_key(first: int, second: int) -> tuple[int, int]:
    return (first, second) if first <= second else (second, first)


def _source_session_id_from_path(path: Path) -> str:
    return path.name or "unknown_session"


__all__ = [
    "COHERENCE_MOTION_CLASSIFIER_ID",
    "COHERENCE_MOTION_CLASSIFIER_VERSION",
    "CoherenceMotionDriftEstimate",
    "CoherenceMotionInferenceResult",
    "estimate_basin_drift_velocities",
    "infer_coherence_motion",
    "infer_coherence_motion_report",
]
