"""Topological-motion observer over checkpoint topology deltas and events."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .motion import (
    MotionCarrierSet,
    MotionEvidence,
    MotionRecord,
    MotionReport,
)
from .motion_loader import MotionTopologyDelta, MotionWindowLoadResult, load_motion_window


TOPOLOGICAL_MOTION_CLASSIFIER_ID = "motion_topological_observer"
TOPOLOGICAL_MOTION_CLASSIFIER_VERSION = "motion_inference_iter7_v1"

_EVENT_BACKED_CONFIDENCE = 0.82
_TOPOLOGY_ONLY_CONFIDENCE = 0.45
_EVENT_ONLY_CONFIDENCE = 0.62
_DIAGNOSTIC_CONFIDENCE_CAP = 0.25

_GROWTH_EVENT_TOKENS = ("growth", "birth", "child_attached")
_SPARK_EXPANSION_EVENT_TOKENS = ("spark", "expansion", "module_created")
_COLLAPSE_EVENT_TOKENS = ("collapse", "choice_resolved")
_SPLIT_EVENT_TOKENS = ("split", "fission", "division")
_MERGE_EVENT_TOKENS = ("merge",)
_PRUNE_EVENT_TOKENS = ("prune", "removal", "removed")


@dataclass(frozen=True)
class TopologicalMotionEventRef:
    """Compact event reference matched to a topology interval."""

    event_id: str
    step_index: int
    event_index: int
    event_kind: str
    event_domain: str | None
    lifecycle_stage: str | None
    topology_mutation: bool | None
    primary_node_id: int | None
    primary_edge_id: int | None

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "event_id": self.event_id,
                "step_index": self.step_index,
                "event_index": self.event_index,
                "event_kind": self.event_kind,
                "event_domain": self.event_domain,
                "lifecycle_stage": self.lifecycle_stage,
                "topology_mutation": self.topology_mutation,
                "primary_node_id": self.primary_node_id,
                "primary_edge_id": self.primary_edge_id,
            }
        )


@dataclass(frozen=True)
class TopologicalMotionDelta:
    """Observed topology mutation over one checkpoint interval."""

    from_checkpoint_id: str
    to_checkpoint_id: str
    from_step: int
    to_step: int
    motion_event: str
    relationship: str
    evidence_mode: str
    born_node_ids: tuple[int, ...]
    removed_node_ids: tuple[int, ...]
    born_edge_ids: tuple[int, ...]
    removed_edge_ids: tuple[int, ...]
    event_refs: tuple[TopologicalMotionEventRef, ...]
    identity_continuity_status: str
    degradation_reasons: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "from_checkpoint_id": self.from_checkpoint_id,
                "to_checkpoint_id": self.to_checkpoint_id,
                "from_step": self.from_step,
                "to_step": self.to_step,
                "motion_event": self.motion_event,
                "relationship": self.relationship,
                "evidence_mode": self.evidence_mode,
                "born_node_ids": list(self.born_node_ids),
                "removed_node_ids": list(self.removed_node_ids),
                "born_edge_ids": list(self.born_edge_ids),
                "removed_edge_ids": list(self.removed_edge_ids),
                "event_refs": [event.to_mapping() for event in self.event_refs],
                "identity_continuity_status": self.identity_continuity_status,
                "degradation_reasons": list(self.degradation_reasons),
            }
        )


@dataclass(frozen=True)
class TopologicalMotionInferenceResult:
    """Topological motion records plus diagnostic deltas."""

    window_load_result: MotionWindowLoadResult
    records: tuple[MotionRecord, ...]
    deltas: tuple[TopologicalMotionDelta, ...]
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
                "classifier_id": TOPOLOGICAL_MOTION_CLASSIFIER_ID,
                "classifier_version": TOPOLOGICAL_MOTION_CLASSIFIER_VERSION,
                "source_runtime_family": (
                    self.window_load_result.landscape_load_result.source_runtime_family
                ),
                "record_count": len(self.records),
                "delta_count": len(self.deltas),
                "diagnostic_only": self.diagnostic_only,
                "motion_window": self.window_load_result.motion_window.to_mapping(),
                "records": [record.to_mapping() for record in self.records],
                "deltas": [delta.to_mapping() for delta in self.deltas],
            }
        )


def infer_topological_motion(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    allow_short_persistence_window: bool = True,
) -> TopologicalMotionInferenceResult:
    """Infer support/topology motion from checkpoint deltas and event rows."""

    load_result = (
        path_or_result
        if isinstance(path_or_result, MotionWindowLoadResult)
        else load_motion_window(
            path_or_result,
            allow_short_persistence_window=allow_short_persistence_window,
        )
    )
    event_refs = tuple(
        _event_ref(row)
        for row in load_result.landscape_load_result.telemetry_pack.event_rows
    )
    deltas: list[TopologicalMotionDelta] = []
    records: list[MotionRecord] = []
    for topology_delta in load_result.topology_deltas:
        matched_events = _matching_events(topology_delta, event_refs)
        topological = _has_topology_change(topology_delta) or _events_indicate_topology(matched_events)
        if not topological:
            continue
        delta = _topological_delta(topology_delta, matched_events)
        deltas.append(delta)
        records.append(_record_for_delta(load_result, delta))
    return TopologicalMotionInferenceResult(
        window_load_result=load_result,
        records=tuple(records),
        deltas=tuple(deltas),
        diagnostic_only=load_result.availability.diagnostic_only,
    )


def infer_topological_motion_report(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    source_session_id: str | None = None,
    source_artifact_paths: Sequence[str] = (),
    **kwargs: Any,
) -> MotionReport:
    """Infer topological motion and return a serializable motion report."""

    result = infer_topological_motion(path_or_result, **kwargs)
    return result.to_report(
        source_session_id=source_session_id,
        source_artifact_paths=source_artifact_paths,
    )


def _topological_delta(
    topology_delta: MotionTopologyDelta,
    event_refs: tuple[TopologicalMotionEventRef, ...],
) -> TopologicalMotionDelta:
    motion_event = _motion_event(topology_delta, event_refs)
    relationship = _relationship_for_motion_event(motion_event)
    evidence_mode = _evidence_mode(topology_delta, event_refs)
    identity_status = _identity_continuity_status(topology_delta)
    degradation_reasons = _degradation_reasons(topology_delta, event_refs)
    return TopologicalMotionDelta(
        from_checkpoint_id=topology_delta.from_checkpoint_id,
        to_checkpoint_id=topology_delta.to_checkpoint_id,
        from_step=topology_delta.from_step,
        to_step=topology_delta.to_step,
        motion_event=motion_event,
        relationship=relationship,
        evidence_mode=evidence_mode,
        born_node_ids=topology_delta.born_node_ids,
        removed_node_ids=topology_delta.removed_node_ids,
        born_edge_ids=topology_delta.born_edge_ids,
        removed_edge_ids=topology_delta.removed_edge_ids,
        event_refs=event_refs,
        identity_continuity_status=identity_status,
        degradation_reasons=degradation_reasons,
    )


def _record_for_delta(
    load_result: MotionWindowLoadResult,
    delta: TopologicalMotionDelta,
) -> MotionRecord:
    confidence = _confidence(load_result, delta)
    edge_ids = tuple(sorted(set(delta.born_edge_ids + delta.removed_edge_ids)))
    node_ids = tuple(sorted(set(delta.born_node_ids + delta.removed_node_ids)))
    return MotionRecord(
        motion_id=(
            f"motion_topological_step{delta.from_step:04d}_{delta.to_step:04d}_"
            f"{delta.motion_event}"
        ),
        classifier_id=TOPOLOGICAL_MOTION_CLASSIFIER_ID,
        classifier_version=TOPOLOGICAL_MOTION_CLASSIFIER_VERSION,
        motion_kind="topological",
        relationship=delta.relationship,
        confidence=confidence,
        evidence_quality=_evidence_quality(load_result, delta, confidence=confidence),
        source_runtime_family=load_result.landscape_load_result.source_runtime_family,
        step_window=(delta.from_step, delta.to_step),
        step_ids=(delta.from_step, delta.to_step),
        old_carriers=_old_carriers(delta),
        new_carriers=_new_carriers(delta),
        evidence=MotionEvidence(
            telemetry_fields=tuple(
                sorted(
                    {
                        "motion_topological.motion_event",
                        "motion_topological.identity_continuity_status",
                        "graph_checkpoints.topology_delta",
                        *(
                            ("events.event_kind", "events.step_index", "events.payload")
                            if delta.event_refs
                            else ()
                        ),
                    }
                )
            ),
            checkpoint_ids=(delta.from_checkpoint_id, delta.to_checkpoint_id),
            step_ids=(delta.from_step, delta.to_step),
            node_ids=node_ids,
            edge_ids=edge_ids,
            event_ids=tuple(event.event_id for event in delta.event_refs),
            budget_accountability="unavailable",
            degradation_reasons=delta.degradation_reasons,
        ),
        non_claims=(
            "no_identity_motion_claim",
            "topology_change_not_identity_walking",
            "not_authored_vs_observed_comparison",
        ),
    )


def _old_carriers(delta: TopologicalMotionDelta) -> MotionCarrierSet:
    if delta.removed_node_ids or delta.removed_edge_ids:
        return MotionCarrierSet(
            node_ids=delta.removed_node_ids,
            edge_ids=delta.removed_edge_ids,
        )
    return MotionCarrierSet(primitive_ids=("pre_topology_support",))


def _new_carriers(delta: TopologicalMotionDelta) -> MotionCarrierSet:
    if delta.born_node_ids or delta.born_edge_ids:
        return MotionCarrierSet(
            node_ids=delta.born_node_ids,
            edge_ids=delta.born_edge_ids,
        )
    if delta.relationship in ("collapsed", "dissolved"):
        return MotionCarrierSet(primitive_ids=("post_topology_support_contracted",))
    return MotionCarrierSet(primitive_ids=("post_topology_support",))


def _confidence(
    load_result: MotionWindowLoadResult,
    delta: TopologicalMotionDelta,
) -> float:
    if load_result.availability.diagnostic_only:
        return _DIAGNOSTIC_CONFIDENCE_CAP
    if delta.evidence_mode == "event_backed_topology_delta":
        return _EVENT_BACKED_CONFIDENCE
    if delta.evidence_mode == "event_only_topology_mutation":
        return _EVENT_ONLY_CONFIDENCE
    return _TOPOLOGY_ONLY_CONFIDENCE


def _evidence_quality(
    load_result: MotionWindowLoadResult,
    delta: TopologicalMotionDelta,
    *,
    confidence: float,
) -> str:
    if load_result.availability.diagnostic_only:
        return "diagnostic_only"
    if delta.evidence_mode == "topology_only":
        return "degraded"
    if confidence >= 0.80:
        return "strong"
    if confidence >= 0.50:
        return "partial"
    return "degraded"


def _motion_event(
    topology_delta: MotionTopologyDelta,
    event_refs: tuple[TopologicalMotionEventRef, ...],
) -> str:
    kinds = tuple(event.event_kind for event in event_refs)
    if _contains_any(kinds, _GROWTH_EVENT_TOKENS):
        return "growth_support_birth"
    if _contains_any(kinds, _COLLAPSE_EVENT_TOKENS):
        return "support_contraction"
    if _contains_any(kinds, _SPLIT_EVENT_TOKENS):
        return "support_split"
    if _contains_any(kinds, _MERGE_EVENT_TOKENS):
        return "support_merge"
    if _contains_any(kinds, _PRUNE_EVENT_TOKENS):
        return "support_prune"
    if _contains_any(kinds, _SPARK_EXPANSION_EVENT_TOKENS):
        return "support_refinement"
    born = bool(topology_delta.born_node_ids or topology_delta.born_edge_ids)
    removed = bool(topology_delta.removed_node_ids or topology_delta.removed_edge_ids)
    if born and removed:
        return "support_reconfiguration"
    if born:
        return "support_birth"
    if removed:
        return "support_removal"
    return "support_reassignment"


def _relationship_for_motion_event(motion_event: str) -> str:
    if motion_event == "support_split":
        return "split"
    if motion_event == "support_merge":
        return "merged"
    if motion_event == "support_contraction":
        return "collapsed"
    if motion_event in ("support_prune", "support_removal"):
        return "dissolved"
    if motion_event in ("support_reconfiguration", "support_reassignment"):
        return "stationary"
    return "emerged"


def _evidence_mode(
    topology_delta: MotionTopologyDelta,
    event_refs: tuple[TopologicalMotionEventRef, ...],
) -> str:
    has_topology = _has_topology_change(topology_delta)
    has_events = bool(event_refs)
    if has_topology and has_events:
        return "event_backed_topology_delta"
    if has_events:
        return "event_only_topology_mutation"
    return "topology_only"


def _identity_continuity_status(topology_delta: MotionTopologyDelta) -> str:
    born = bool(topology_delta.born_node_ids or topology_delta.born_edge_ids)
    removed = bool(topology_delta.removed_node_ids or topology_delta.removed_edge_ids)
    if born and removed:
        return "requires_identity_matcher"
    if born:
        return "prior_identity_unclaimed"
    if removed:
        return "successor_identity_unclaimed"
    return "event_indicates_topology_without_checkpoint_carrier_delta"


def _degradation_reasons(
    topology_delta: MotionTopologyDelta,
    event_refs: tuple[TopologicalMotionEventRef, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if _has_topology_change(topology_delta) and not event_refs:
        reasons.append("topology_only_no_matching_event_row")
    if event_refs and not _has_topology_change(topology_delta):
        reasons.append("event_only_no_checkpoint_topology_delta")
    if not any(event.topology_mutation is True for event in event_refs) and event_refs:
        reasons.append("event_topology_mutation_flag_unavailable_or_false")
    return tuple(sorted(set(reasons)))


def _matching_events(
    topology_delta: MotionTopologyDelta,
    event_refs: Sequence[TopologicalMotionEventRef],
) -> tuple[TopologicalMotionEventRef, ...]:
    return tuple(
        event
        for event in event_refs
        if topology_delta.from_step < event.step_index <= topology_delta.to_step
        and _is_topological_event(event)
    )


def _event_ref(row: Any) -> TopologicalMotionEventRef:
    extension = _family_extension(row)
    return TopologicalMotionEventRef(
        event_id=f"step{int(row.step_index):04d}_event{int(row.event_index):04d}_{row.event_kind}",
        step_index=int(row.step_index),
        event_index=int(row.event_index),
        event_kind=str(row.event_kind),
        event_domain=_optional_str(extension.get("event_domain")),
        lifecycle_stage=_optional_str(extension.get("lifecycle_stage")),
        topology_mutation=_optional_bool(extension.get("topology_mutation")),
        primary_node_id=_primary_int(row.payload, extension, ("primary_node_id", "node_id", "candidate_node_id", "sink_node_id", "parent_node_id", "child_node_id")),
        primary_edge_id=_primary_int(row.payload, extension, ("primary_edge_id", "edge_id")),
    )


def _family_extension(row: Any) -> Mapping[str, Any]:
    if row.source_family and row.source_family in row.family_extensions:
        return row.family_extensions[row.source_family]
    for value in row.family_extensions.values():
        if isinstance(value, Mapping):
            return value
    return {}


def _is_topological_event(event: TopologicalMotionEventRef) -> bool:
    if event.topology_mutation is True:
        return True
    tokens = (
        _GROWTH_EVENT_TOKENS
        + _SPARK_EXPANSION_EVENT_TOKENS
        + _COLLAPSE_EVENT_TOKENS
        + _SPLIT_EVENT_TOKENS
        + _MERGE_EVENT_TOKENS
        + _PRUNE_EVENT_TOKENS
    )
    return _contains_any((event.event_kind, event.event_domain or "", event.lifecycle_stage or ""), tokens)


def _events_indicate_topology(events: Sequence[TopologicalMotionEventRef]) -> bool:
    return any(_is_topological_event(event) for event in events)


def _has_topology_change(delta: MotionTopologyDelta) -> bool:
    return bool(
        delta.born_node_ids
        or delta.removed_node_ids
        or delta.born_edge_ids
        or delta.removed_edge_ids
    )


def _contains_any(values: Sequence[str], tokens: Sequence[str]) -> bool:
    lowered = " ".join(value.lower() for value in values)
    return any(token in lowered for token in tokens)


def _primary_int(
    payload: Mapping[str, Any],
    extension: Mapping[str, Any],
    keys: Sequence[str],
) -> int | None:
    for mapping in (extension, payload):
        for key in keys:
            value = mapping.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                return value
    return None


def _optional_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _source_session_id_from_path(path: Path) -> str:
    return path.name or "unknown_session"


__all__ = [
    "TOPOLOGICAL_MOTION_CLASSIFIER_ID",
    "TOPOLOGICAL_MOTION_CLASSIFIER_VERSION",
    "TopologicalMotionDelta",
    "TopologicalMotionEventRef",
    "TopologicalMotionInferenceResult",
    "infer_topological_motion",
    "infer_topological_motion_report",
]
