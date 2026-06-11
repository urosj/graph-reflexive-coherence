"""Observed ridge/boundary classifier for landscape inference."""

from __future__ import annotations

from collections.abc import Sequence
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
    LandscapeInferenceEvidenceSubstrate,
    LandscapeInferenceNodeEvidence,
    build_landscape_inference_evidence_substrate,
)
from .seed import LandscapePrimitive, LandscapeSeed, RidgeSeedPrimitive


RIDGE_CLASSIFIER_ID = "landscape_inference_ridge_classifier"
RIDGE_CLASSIFIER_VERSION = "landscape_inference_iter5_v1"


@dataclass(frozen=True)
class LandscapeInferenceRidgeCandidate:
    """Checkpoint-local ridge candidate assembled from node evidence."""

    candidate_id: str
    node_id: int
    checkpoint_ids: tuple[str, ...]
    persistence_steps: int
    gradient_norm: float | None
    tensor_anisotropy: float | None
    tensor_trace: float | None
    incident_abs_flux: float | None
    occupied_port_count: int | None
    free_port_count: int | None
    boundary_port_evidence: bool
    pressure_boundary_label_present: bool
    evidence_mode: str
    role: str
    ridge_kind: str
    status: str
    rejection_reason: str | None
    confidence: float
    evidence_limitations: tuple[str, ...]
    evidence_fields: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "candidate_id": self.candidate_id,
                "node_id": self.node_id,
                "checkpoint_ids": list(self.checkpoint_ids),
                "persistence_steps": self.persistence_steps,
                "gradient_norm": self.gradient_norm,
                "tensor_anisotropy": self.tensor_anisotropy,
                "tensor_trace": self.tensor_trace,
                "incident_abs_flux": self.incident_abs_flux,
                "occupied_port_count": self.occupied_port_count,
                "free_port_count": self.free_port_count,
                "boundary_port_evidence": self.boundary_port_evidence,
                "pressure_boundary_label_present": self.pressure_boundary_label_present,
                "evidence_mode": self.evidence_mode,
                "role": self.role,
                "ridge_kind": self.ridge_kind,
                "status": self.status,
                "rejection_reason": self.rejection_reason,
                "confidence": self.confidence,
                "evidence_limitations": list(self.evidence_limitations),
                "evidence_fields": list(self.evidence_fields),
            }
        )


def infer_landscape_ridge_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
) -> LandscapeSeed:
    """Return a normal `LandscapeSeed` with observed ridge primitives added."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates = classify_landscape_ridge_candidates(
        resolved_substrate,
        runtime_family=load_result.source_runtime_family,
    )
    accepted = tuple(candidate for candidate in candidates if candidate.status == "accepted")
    primitives: list[LandscapePrimitive] = list(load_result.inferred_seed.primitives)
    emerged_ids: list[str] = []
    for candidate in accepted:
        primitive_id = f"observed_ridge_{_safe_id(candidate.candidate_id)}"
        emerged_ids.append(primitive_id)
        extension = LandscapeInferencePrimitiveExtension(
            authority="observed",
            classifier_id=RIDGE_CLASSIFIER_ID,
            classifier_version=RIDGE_CLASSIFIER_VERSION,
            confidence=candidate.confidence,
            source_runtime_family=load_result.source_runtime_family,
            observed_from=LandscapeInferenceObservedFrom(
                session_id=_source_session_id_from_path(load_result.artifact_root),
                run_id=load_result.telemetry_pack.run_summary.identity.run_id,
                artifact_root=str(load_result.artifact_root),
                step_window=(
                    load_result.inference_window.start_step,
                    load_result.inference_window.end_step,
                ),
            ),
            evidence=LandscapeInferenceEvidence(
                telemetry_fields=candidate.evidence_fields,
                checkpoint_ids=candidate.checkpoint_ids,
                node_ids=(candidate.node_id,),
            ),
            matched_authored_primitive_id=None,
            relationship_to_authored="emerged",
        )
        primitives.append(
            RidgeSeedPrimitive(
                id=primitive_id,
                role=candidate.role,
                tags=["observed", "landscape_inference", candidate.evidence_mode],
                ridge_kind=candidate.ridge_kind,
                anisotropy_hint={
                    "gradient_norm": candidate.gradient_norm,
                    "tensor_anisotropy": candidate.tensor_anisotropy,
                    "tensor_trace": candidate.tensor_trace,
                },
                permeability_hint={
                    "incident_abs_flux": candidate.incident_abs_flux,
                    "boundary_port_evidence": candidate.boundary_port_evidence,
                },
                extensions={
                    "landscape_inference": landscape_inference_primitive_mapping(extension),
                    "landscape_inference_ridge": candidate.to_mapping(),
                },
            )
        )
    extensions = dict(load_result.inferred_seed.extensions)
    extensions["landscape_inference_ridge_summary"] = canonicalize_json_value(
        {
            "classifier_id": RIDGE_CLASSIFIER_ID,
            "classifier_version": RIDGE_CLASSIFIER_VERSION,
            "runtime_family": load_result.source_runtime_family,
            "candidate_count": len(candidates),
            "observed_ridge_count": len(accepted),
            "emerged_observed_ridge_ids": sorted(emerged_ids),
            "rejected_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "rejected"
            ),
            "ambiguous_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "ambiguous"
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


def classify_landscape_ridge_candidates(
    substrate: LandscapeInferenceEvidenceSubstrate,
    *,
    runtime_family: str,
    gradient_threshold: float = 1.0,
    tensor_anisotropy_threshold: float = 1.0,
    low_throughflow_threshold: float = 0.1,
) -> tuple[LandscapeInferenceRidgeCandidate, ...]:
    """Classify observed ridge candidates from final checkpoint node evidence."""

    del runtime_family
    if not substrate.checkpoint_graphs:
        return ()
    final_graph = substrate.checkpoint_graphs[-1]
    candidates: list[LandscapeInferenceRidgeCandidate] = []
    for node_id, node in sorted(final_graph.nodes.items()):
        if not _has_any_ridge_relevant_evidence(node):
            continue
        incident_abs_flux = _incident_abs_flux(final_graph, node_id)
        occupied_ports, free_ports = _port_counts(node)
        persistence_steps = _node_persistence_steps(substrate, node_id)
        boundary_port_evidence = (
            occupied_ports is not None
            and free_ports is not None
            and occupied_ports > 0
            and free_ports > 0
        )
        pressure_label = _pressure_boundary_label_present(node)
        status, reason, confidence, evidence_mode, role, ridge_kind, limitations = _ridge_status(
            node,
            persistence_steps=persistence_steps,
            checkpoint_count=len(substrate.checkpoint_graphs),
            incident_abs_flux=incident_abs_flux,
            boundary_port_evidence=boundary_port_evidence,
            pressure_boundary_label_present=pressure_label,
            diagnostic_only=substrate.diagnostic_only,
            gradient_threshold=gradient_threshold,
            tensor_anisotropy_threshold=tensor_anisotropy_threshold,
            low_throughflow_threshold=low_throughflow_threshold,
        )
        candidates.append(
            LandscapeInferenceRidgeCandidate(
                candidate_id=f"node_{node_id}",
                node_id=node_id,
                checkpoint_ids=tuple(
                    graph.checkpoint_id
                    for graph in substrate.checkpoint_graphs
                    if node_id in graph.nodes
                ),
                persistence_steps=persistence_steps,
                gradient_norm=node.gradient_norm,
                tensor_anisotropy=node.tensor_anisotropy,
                tensor_trace=node.tensor_trace,
                incident_abs_flux=incident_abs_flux,
                occupied_port_count=occupied_ports,
                free_port_count=free_ports,
                boundary_port_evidence=boundary_port_evidence,
                pressure_boundary_label_present=pressure_label,
                evidence_mode=evidence_mode,
                role=role,
                ridge_kind=ridge_kind,
                status=status,
                rejection_reason=reason,
                confidence=confidence,
                evidence_limitations=limitations,
                evidence_fields=_ridge_evidence_fields(
                    node,
                    incident_abs_flux=incident_abs_flux,
                    boundary_port_evidence=boundary_port_evidence,
                    pressure_boundary_label_present=pressure_label,
                ),
            )
        )
    return tuple(candidates)


def _ridge_status(
    node: LandscapeInferenceNodeEvidence,
    *,
    persistence_steps: int,
    checkpoint_count: int,
    incident_abs_flux: float | None,
    boundary_port_evidence: bool,
    pressure_boundary_label_present: bool,
    diagnostic_only: bool,
    gradient_threshold: float,
    tensor_anisotropy_threshold: float,
    low_throughflow_threshold: float,
) -> tuple[str, str | None, float, str, str, str, tuple[str, ...]]:
    limitations: list[str] = []
    gradient_pass = node.gradient_norm is not None and node.gradient_norm >= gradient_threshold
    tensor_pass = (
        node.tensor_anisotropy is not None
        and node.tensor_anisotropy >= tensor_anisotropy_threshold
    )
    if not gradient_pass and not tensor_pass:
        if pressure_boundary_label_present:
            return (
                "rejected",
                "pressure_boundary_label_without_geometric_ridge_evidence",
                0.0,
                "insufficient_pressure_boundary_label_only",
                "boundary_ridge",
                "geometric_ridge",
                ("pressure_boundary_is_frontier_not_ridge",),
            )
        return (
            "rejected",
            "missing_gradient_or_tensor_ridge_evidence",
            0.0,
            "insufficient_evidence",
            "boundary_ridge",
            "geometric_ridge",
            ("requires_checkpoint_node_gradient_or_tensor_evidence",),
        )
    if persistence_steps < checkpoint_count:
        return (
            "rejected",
            "ridge_node_not_persistent_across_window",
            0.0,
            "ruptured_ridge_candidate",
            "boundary_ridge",
            "geometric_ridge",
            ("node_removed_or_merged_during_window",),
        )
    if incident_abs_flux is None:
        limitations.append("throughflow_unavailable")
    elif incident_abs_flux > low_throughflow_threshold:
        limitations.append("low_leakage_not_established")
    if not boundary_port_evidence:
        limitations.append("port_boundary_evidence_unavailable")
    if diagnostic_only:
        limitations.append("short_persistence_window")
    confidence = 0.72
    if gradient_pass and tensor_pass:
        confidence = 0.86
        evidence_mode = "gradient_tensor_ridge"
    elif gradient_pass:
        evidence_mode = "gradient_ridge"
    else:
        evidence_mode = "tensor_anisotropy_ridge"
    if incident_abs_flux is not None and incident_abs_flux <= low_throughflow_threshold:
        confidence += 0.04
    if boundary_port_evidence:
        confidence += 0.04
    if diagnostic_only:
        confidence -= 0.2
        status = "ambiguous"
        reason = "short_persistence_window"
    else:
        status = "accepted"
        reason = None
    return (
        status,
        reason,
        max(0.0, min(1.0, confidence)),
        evidence_mode,
        "boundary_ridge",
        "geometric_ridge",
        tuple(limitations),
    )


def _has_any_ridge_relevant_evidence(node: LandscapeInferenceNodeEvidence) -> bool:
    return bool(
        node.gradient_norm is not None
        or node.tensor_anisotropy is not None
        or node.tensor_trace is not None
        or node.port_matrix is not None
        or _pressure_boundary_label_present(node)
    )


def _incident_abs_flux(graph: Any, node_id: int) -> float | None:
    values: list[float] = []
    for neighbor_id in graph.adjacency.get(node_id, ()):
        edge_id = graph.edge_id_by_pair.get(tuple(sorted((node_id, neighbor_id))))
        if edge_id is None:
            continue
        signed_flux = graph.edges[edge_id].signed_flux
        if signed_flux is not None:
            values.append(abs(float(signed_flux)))
    return None if not values else float(sum(values))


def _port_counts(node: LandscapeInferenceNodeEvidence) -> tuple[int | None, int | None]:
    if node.port_matrix is None:
        return (None, None)
    occupied = sum(1 for row in node.port_matrix for item in row if item)
    return (occupied, 9 - occupied)


def _node_persistence_steps(
    substrate: LandscapeInferenceEvidenceSubstrate,
    node_id: int,
) -> int:
    return sum(1 for graph in substrate.checkpoint_graphs if node_id in graph.nodes)


def _pressure_boundary_label_present(node: LandscapeInferenceNodeEvidence) -> bool:
    for mapping in (node.payload, node.provenance):
        values = tuple(str(value) for value in mapping.values())
        if any("pressure_boundary" in value for value in values):
            return True
        if any("frontier" in value or "front_capacity" in value for value in values):
            return True
    return False


def _ridge_evidence_fields(
    node: LandscapeInferenceNodeEvidence,
    *,
    incident_abs_flux: float | None,
    boundary_port_evidence: bool,
    pressure_boundary_label_present: bool,
) -> tuple[str, ...]:
    fields: list[str] = ["graph_checkpoints.node_records.node_id"]
    if node.gradient_norm is not None:
        fields.append("graph_checkpoints.node_records.gradient_norm")
    if node.tensor_anisotropy is not None:
        fields.append("graph_checkpoints.node_records.tensor_anisotropy")
    if node.tensor_trace is not None:
        fields.append("graph_checkpoints.node_records.tensor_trace")
    if incident_abs_flux is not None:
        fields.append("graph_checkpoints.edge_records.signed_flux")
    if boundary_port_evidence:
        fields.append("graph_checkpoints.node_records.port_matrix")
    if pressure_boundary_label_present:
        fields.append("graph_checkpoints.node_records.pressure_boundary_label")
    return tuple(fields)


def _safe_id(value: object) -> str:
    text = str(value).strip().lower().replace("-", "_")
    return "".join(char if char.isalnum() or char == "_" else "_" for char in text).strip("_") or "unknown"


__all__ = [
    "LandscapeInferenceRidgeCandidate",
    "RIDGE_CLASSIFIER_ID",
    "RIDGE_CLASSIFIER_VERSION",
    "classify_landscape_ridge_candidates",
    "infer_landscape_ridge_seed",
]
