"""Observed junction/saddle/event classifiers for landscape inference."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference import (
    LandscapeInferenceEvidence,
    LandscapeInferenceObservedFrom,
    LandscapeInferencePrimitiveExtension,
    landscape_inference_primitive_mapping,
)
from .inference_basin import _source_session_id_from_path
from .inference_loader import LandscapeInferenceArtifactLoadResult
from .inference_substrate import (
    LandscapeInferenceCheckpointGraph,
    LandscapeInferenceEvidenceSubstrate,
    LandscapeInferenceNodeEvidence,
    build_landscape_inference_evidence_substrate,
)
from .seed import JunctionSeedPrimitive, LandscapePrimitive, LandscapeSeed


JUNCTION_CLASSIFIER_ID = "landscape_inference_junction_classifier"
JUNCTION_CLASSIFIER_VERSION = "landscape_inference_iter6_v1"

_CHOICE_EVENT_KINDS = frozenset(("choice_detected", "collapse"))
_SPARK_EVENT_KINDS = frozenset(("spark_candidate", "hybrid_spark_candidate"))


@dataclass(frozen=True)
class LandscapeInferenceJunctionCandidate:
    """Observed junction or saddle candidate assembled from checkpoints/events."""

    candidate_id: str
    primitive_type: str
    role: str
    node_id: int | None
    checkpoint_ids: tuple[str, ...]
    event_refs: tuple[str, ...]
    step_window: tuple[int, int]
    evidence_mode: str
    status: str
    rejection_reason: str | None
    confidence: float
    occupied_port_count: int | None
    free_port_count: int | None
    incident_edge_count: int | None
    active_flux_edge_count: int | None
    branch_node_ids: tuple[int, ...]
    evidence_fields: tuple[str, ...]
    evidence_limitations: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "candidate_id": self.candidate_id,
                "primitive_type": self.primitive_type,
                "role": self.role,
                "node_id": self.node_id,
                "checkpoint_ids": list(self.checkpoint_ids),
                "event_refs": list(self.event_refs),
                "step_window": list(self.step_window),
                "evidence_mode": self.evidence_mode,
                "status": self.status,
                "rejection_reason": self.rejection_reason,
                "confidence": self.confidence,
                "occupied_port_count": self.occupied_port_count,
                "free_port_count": self.free_port_count,
                "incident_edge_count": self.incident_edge_count,
                "active_flux_edge_count": self.active_flux_edge_count,
                "branch_node_ids": list(self.branch_node_ids),
                "evidence_fields": list(self.evidence_fields),
                "evidence_limitations": list(self.evidence_limitations),
            }
        )


def infer_landscape_junction_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
) -> LandscapeSeed:
    """Return a normal `LandscapeSeed` with observed junction/saddle primitives."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates = classify_landscape_junction_candidates(
        load_result,
        substrate=resolved_substrate,
    )
    accepted = tuple(candidate for candidate in candidates if candidate.status == "accepted")
    primitives: list[LandscapePrimitive] = list(load_result.inferred_seed.primitives)
    emerged_ids: list[str] = []
    for candidate in accepted:
        primitive_id = f"observed_{candidate.primitive_type}_{_safe_id(candidate.candidate_id)}"
        emerged_ids.append(primitive_id)
        extension = LandscapeInferencePrimitiveExtension(
            authority="observed",
            classifier_id=JUNCTION_CLASSIFIER_ID,
            classifier_version=JUNCTION_CLASSIFIER_VERSION,
            confidence=candidate.confidence,
            source_runtime_family=load_result.source_runtime_family,
            observed_from=LandscapeInferenceObservedFrom(
                session_id=_source_session_id_from_path(load_result.artifact_root),
                run_id=load_result.telemetry_pack.run_summary.identity.run_id,
                artifact_root=str(load_result.artifact_root),
                step_window=candidate.step_window,
            ),
            evidence=LandscapeInferenceEvidence(
                telemetry_fields=candidate.evidence_fields,
                checkpoint_ids=candidate.checkpoint_ids,
                node_ids=() if candidate.node_id is None else (candidate.node_id,),
            ),
            matched_authored_primitive_id=None,
            relationship_to_authored="emerged",
        )
        primitives.append(
            JunctionSeedPrimitive(
                id=primitive_id,
                type=candidate.primitive_type,
                role=candidate.role,
                junction_role=candidate.role,
                tags=["observed", "landscape_inference", candidate.evidence_mode],
                hints={
                    "runtime_node_id": candidate.node_id,
                    "event_refs": list(candidate.event_refs),
                    "branch_node_ids": list(candidate.branch_node_ids),
                    "checkpoint_ids": list(candidate.checkpoint_ids),
                },
                extensions={
                    "landscape_inference": landscape_inference_primitive_mapping(extension),
                    "landscape_inference_junction": candidate.to_mapping(),
                },
            )
        )
    extensions = dict(load_result.inferred_seed.extensions)
    extensions["landscape_inference_junction_summary"] = canonicalize_json_value(
        {
            "classifier_id": JUNCTION_CLASSIFIER_ID,
            "classifier_version": JUNCTION_CLASSIFIER_VERSION,
            "runtime_family": load_result.source_runtime_family,
            "candidate_count": len(candidates),
            "observed_primitive_count": len(accepted),
            "observed_junction_count": sum(
                1
                for candidate in accepted
                if candidate.primitive_type == "junction"
            ),
            "observed_saddle_count": sum(
                1
                for candidate in accepted
                if candidate.primitive_type == "saddle"
            ),
            "emerged_observed_ids": sorted(emerged_ids),
            "rejected_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "rejected"
            ),
        }
    )
    return LandscapeSeed(
        seed_schema=load_result.inferred_seed.seed_schema,
        seed_version=load_result.inferred_seed.seed_version,
        meta=load_result.inferred_seed.meta,
        constitutive_profile=load_result.inferred_seed.constitutive_profile,
        primitives=primitives,
        transport_intent=list(load_result.inferred_seed.transport_intent),
        geometry_hints=load_result.inferred_seed.geometry_hints,
        extensions=extensions,
    )


def classify_landscape_junction_candidates(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    active_flux_threshold: float = 1e-12,
    curvature_degeneracy_threshold: float = 1e-6,
) -> tuple[LandscapeInferenceJunctionCandidate, ...]:
    """Classify junction and saddle candidates from checkpoint/event evidence."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates: dict[str, LandscapeInferenceJunctionCandidate] = {}
    final_graph = resolved_substrate.checkpoint_graphs[-1] if resolved_substrate.checkpoint_graphs else None
    if final_graph is not None:
        for candidate in _checkpoint_port_candidates(
            resolved_substrate,
            final_graph,
            active_flux_threshold=active_flux_threshold,
        ):
            candidates[candidate.candidate_id] = candidate
        for candidate in _curvature_saddle_candidates(
            resolved_substrate,
            final_graph,
            curvature_degeneracy_threshold=curvature_degeneracy_threshold,
        ):
            candidates.setdefault(candidate.candidate_id, candidate)
    for candidate in _event_candidates(load_result, resolved_substrate, final_graph):
        existing = candidates.get(candidate.candidate_id)
        if existing is None or _event_candidate_priority(candidate) > _event_candidate_priority(existing):
            candidates[candidate.candidate_id] = candidate
    return tuple(candidates[key] for key in sorted(candidates))


def _checkpoint_port_candidates(
    substrate: LandscapeInferenceEvidenceSubstrate,
    final_graph: LandscapeInferenceCheckpointGraph,
    *,
    active_flux_threshold: float,
) -> tuple[LandscapeInferenceJunctionCandidate, ...]:
    candidates: list[LandscapeInferenceJunctionCandidate] = []
    for node_id, node in sorted(final_graph.nodes.items()):
        if node.port_matrix is None:
            continue
        occupied, free = _port_counts(node)
        incident_edges = _incident_edges(final_graph, node_id)
        active_flux_edges = tuple(
            edge
            for edge in incident_edges
            if edge.signed_flux is not None and abs(edge.signed_flux) > active_flux_threshold
        )
        branch_node_ids = tuple(sorted(final_graph.adjacency.get(node_id, ())))
        if len(branch_node_ids) >= 3 and len(active_flux_edges) >= 2:
            role = "router"
            evidence_mode = "checkpoint_port_flux_router"
            confidence = 0.78
            fields = (
                "graph_checkpoints.node_records.port_matrix",
                "graph_checkpoints.edge_records.signed_flux",
                "graph_checkpoints.edge_records.source_node_id",
                "graph_checkpoints.edge_records.target_node_id",
            )
        elif occupied > 0 and free > 0 and incident_edges:
            role = "gate"
            evidence_mode = "checkpoint_port_gate"
            confidence = 0.66 if active_flux_edges else 0.58
            fields = (
                "graph_checkpoints.node_records.port_matrix",
                "graph_checkpoints.edge_records.signed_flux",
            )
        else:
            continue
        candidates.append(
            LandscapeInferenceJunctionCandidate(
                candidate_id=f"{role}_node_{node_id}",
                primitive_type="junction",
                role=role,
                node_id=node_id,
                checkpoint_ids=_node_checkpoint_ids(substrate, node_id),
                event_refs=(),
                step_window=_full_window(substrate),
                evidence_mode=evidence_mode,
                status="accepted",
                rejection_reason=None,
                confidence=confidence,
                occupied_port_count=occupied,
                free_port_count=free,
                incident_edge_count=len(incident_edges),
                active_flux_edge_count=len(active_flux_edges),
                branch_node_ids=branch_node_ids,
                evidence_fields=fields,
                evidence_limitations=()
                if active_flux_edges
                else ("port_pattern_without_active_flux",),
            )
        )
    return tuple(candidates)


def _curvature_saddle_candidates(
    substrate: LandscapeInferenceEvidenceSubstrate,
    final_graph: LandscapeInferenceCheckpointGraph,
    *,
    curvature_degeneracy_threshold: float,
) -> tuple[LandscapeInferenceJunctionCandidate, ...]:
    candidates: list[LandscapeInferenceJunctionCandidate] = []
    for node_id, node in sorted(final_graph.nodes.items()):
        if node.min_signed_hessian is None:
            continue
        if node.min_signed_hessian > curvature_degeneracy_threshold:
            continue
        candidates.append(
            LandscapeInferenceJunctionCandidate(
                candidate_id=f"curvature_saddle_node_{node_id}",
                primitive_type="saddle",
                role="curvature_degeneracy",
                node_id=node_id,
                checkpoint_ids=_node_checkpoint_ids(substrate, node_id),
                event_refs=(),
                step_window=_full_window(substrate),
                evidence_mode="checkpoint_curvature_degeneracy",
                status="accepted",
                rejection_reason=None,
                confidence=0.7,
                occupied_port_count=_port_counts(node)[0] if node.port_matrix is not None else None,
                free_port_count=_port_counts(node)[1] if node.port_matrix is not None else None,
                incident_edge_count=len(_incident_edges(final_graph, node_id)),
                active_flux_edge_count=None,
                branch_node_ids=tuple(sorted(final_graph.adjacency.get(node_id, ()))),
                evidence_fields=("graph_checkpoints.node_records.min_signed_hessian",),
                evidence_limitations=()
                if node.port_matrix is not None
                else ("port_matrix_unavailable",),
            )
        )
    return tuple(candidates)


def _event_candidates(
    load_result: LandscapeInferenceArtifactLoadResult,
    substrate: LandscapeInferenceEvidenceSubstrate,
    final_graph: LandscapeInferenceCheckpointGraph | None,
) -> tuple[LandscapeInferenceJunctionCandidate, ...]:
    grouped: dict[tuple[str, int | None], list[Any]] = {}
    for row in load_result.telemetry_pack.event_rows:
        kind = str(row.event_kind)
        if kind not in _CHOICE_EVENT_KINDS and kind not in _SPARK_EVENT_KINDS:
            continue
        node_id = _primary_node_id(row)
        role = "collapse_site" if kind in _CHOICE_EVENT_KINDS else "spark_candidate"
        grouped.setdefault((role, node_id), []).append(row)
    candidates: list[LandscapeInferenceJunctionCandidate] = []
    for (role, node_id), rows in sorted(
        grouped.items(),
        key=lambda item: (item[0][0], -1 if item[0][1] is None else item[0][1]),
    ):
        event_refs = tuple(_event_ref(row) for row in rows)
        checkpoint_ids = _node_checkpoint_ids(substrate, node_id) if node_id is not None else ()
        node = None if final_graph is None or node_id is None else final_graph.nodes.get(node_id)
        branch_node_ids = (
            ()
            if final_graph is None or node_id is None
            else tuple(sorted(final_graph.adjacency.get(node_id, ())))
        )
        primitive_type = "junction" if role == "collapse_site" else "saddle"
        candidates.append(
            LandscapeInferenceJunctionCandidate(
                candidate_id=f"{role}_node_{node_id if node_id is not None else 'event'}",
                primitive_type=primitive_type,
                role=role,
                node_id=node_id,
                checkpoint_ids=checkpoint_ids,
                event_refs=event_refs,
                step_window=(min(row.step_index for row in rows), max(row.step_index for row in rows)),
                evidence_mode="event_backed",
                status="accepted",
                rejection_reason=None,
                confidence=0.88 if role == "collapse_site" else 0.84,
                occupied_port_count=_port_counts(node)[0]
                if node is not None and node.port_matrix is not None
                else None,
                free_port_count=_port_counts(node)[1]
                if node is not None and node.port_matrix is not None
                else None,
                incident_edge_count=len(_incident_edges(final_graph, node_id))
                if final_graph is not None and node_id is not None
                else None,
                active_flux_edge_count=None,
                branch_node_ids=branch_node_ids,
                evidence_fields=_event_evidence_fields(role),
                evidence_limitations=()
                if node_id is not None
                else ("event_primary_node_unavailable",),
            )
        )
    return tuple(candidates)


def _event_candidate_priority(candidate: LandscapeInferenceJunctionCandidate) -> int:
    if candidate.evidence_mode == "event_backed":
        return 3
    if candidate.role == "router":
        return 2
    return 1


def _primary_node_id(row: Any) -> int | None:
    family_extensions = _mapping(row.family_extensions)
    for family in family_extensions.values():
        mapping = _mapping(family)
        value = _optional_int(mapping.get("primary_node_id"))
        if value is not None:
            return value
        for key in ("spark_evidence", "choice_collapse_evidence"):
            nested = _mapping(mapping.get(key))
            for nested_key in ("candidate_node_id", "node_id", "sink_node_id"):
                value = _optional_int(nested.get(nested_key))
                if value is not None:
                    return value
    payload = _mapping(row.payload)
    for key in ("primary_node_id", "candidate_node_id", "node_id", "sink_node_id", "parent_node_id"):
        value = _optional_int(payload.get(key))
        if value is not None:
            return value
    return None


def _event_ref(row: Any) -> str:
    return f"step_{int(row.step_index)}:event_{int(row.event_index)}:{row.event_kind}"


def _event_evidence_fields(role: str) -> tuple[str, ...]:
    if role == "collapse_site":
        return (
            "events.event_kind",
            "events.payload.node_id",
            "events.family_extensions.*.choice_collapse_evidence",
        )
    return (
        "events.event_kind",
        "events.payload.candidate_node_id",
        "events.family_extensions.*.spark_evidence",
    )


def _port_counts(node: LandscapeInferenceNodeEvidence) -> tuple[int, int]:
    if node.port_matrix is None:
        return (0, 0)
    occupied = sum(1 for row in node.port_matrix for item in row if item)
    return (occupied, 9 - occupied)


def _incident_edges(
    graph: LandscapeInferenceCheckpointGraph | None,
    node_id: int | None,
) -> tuple[Any, ...]:
    if graph is None or node_id is None:
        return ()
    edge_ids = []
    for neighbor_id in graph.adjacency.get(node_id, ()):
        edge_id = graph.edge_id_by_pair.get(tuple(sorted((node_id, neighbor_id))))
        if edge_id is not None:
            edge_ids.append(edge_id)
    return tuple(graph.edges[edge_id] for edge_id in sorted(edge_ids))


def _node_checkpoint_ids(
    substrate: LandscapeInferenceEvidenceSubstrate,
    node_id: int | None,
) -> tuple[str, ...]:
    if node_id is None:
        return ()
    return tuple(graph.checkpoint_id for graph in substrate.checkpoint_graphs if node_id in graph.nodes)


def _full_window(substrate: LandscapeInferenceEvidenceSubstrate) -> tuple[int, int]:
    return (substrate.inference_window.start_step, substrate.inference_window.end_step)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_id(value: object) -> str:
    text = str(value).strip().lower().replace("-", "_")
    return "".join(char if char.isalnum() or char == "_" else "_" for char in text).strip("_") or "unknown"


__all__ = [
    "JUNCTION_CLASSIFIER_ID",
    "JUNCTION_CLASSIFIER_VERSION",
    "LandscapeInferenceJunctionCandidate",
    "classify_landscape_junction_candidates",
    "infer_landscape_junction_seed",
]
