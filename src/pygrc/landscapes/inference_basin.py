"""Observed basin classifier for landscape inference."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference import (
    LandscapeInferenceEvidence,
    LandscapeInferenceObservedFrom,
    LandscapeInferencePrimitiveExtension,
    landscape_inference_primitive_mapping,
)
from .inference_loader import LandscapeInferenceArtifactLoadResult
from .inference_substrate import (
    LandscapeInferenceCheckpointGraph,
    LandscapeInferenceEvidenceSubstrate,
    LandscapeInferenceNodeEvidence,
    build_landscape_inference_evidence_substrate,
)
from .seed import BasinSeedPrimitive, LandscapePrimitive, LandscapeSeed


BASIN_CLASSIFIER_ID = "landscape_inference_basin_classifier"
BASIN_CLASSIFIER_VERSION = "landscape_inference_iter3_v1"


@dataclass(frozen=True)
class LandscapeInferenceBasinCandidate:
    """Internal basin candidate assembled from checkpoint evidence."""

    basin_id: str
    representative_node_id: int
    member_node_ids: tuple[int, ...]
    checkpoint_ids: tuple[str, ...]
    persistence_steps: int
    evidence_mode: str
    confidence: float
    role: str
    basin_mass: float | None
    basin_mass_source: str
    gradient_norm: float | None
    min_signed_hessian: float | None
    capability_level: str
    evidence_fields: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "basin_id": self.basin_id,
                "representative_node_id": self.representative_node_id,
                "member_node_ids": list(self.member_node_ids),
                "checkpoint_ids": list(self.checkpoint_ids),
                "persistence_steps": self.persistence_steps,
                "evidence_mode": self.evidence_mode,
                "confidence": self.confidence,
                "role": self.role,
                "basin_mass": self.basin_mass,
                "basin_mass_source": self.basin_mass_source,
                "gradient_norm": self.gradient_norm,
                "min_signed_hessian": self.min_signed_hessian,
                "capability_level": self.capability_level,
                "evidence_fields": list(self.evidence_fields),
            }
        )


def infer_landscape_basin_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    authored_seed: LandscapeSeed | None = None,
) -> LandscapeSeed:
    """Return a normal `LandscapeSeed` with observed basin primitives added."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates = classify_landscape_basin_candidates(
        resolved_substrate,
        runtime_family=load_result.source_runtime_family,
    )
    authored_by_id = _authored_basin_primitives_by_id(authored_seed)
    preserved_authored_ids: list[str] = []
    emerged_observed_ids: list[str] = []
    primitives: list[LandscapePrimitive] = list(load_result.inferred_seed.primitives)
    for candidate in candidates:
        primitive_id = f"observed_basin_{_safe_id(candidate.basin_id)}"
        matched_id = primitive_id if primitive_id in authored_by_id else None
        relationship = "preserved" if matched_id is not None else "emerged"
        if matched_id is not None:
            preserved_authored_ids.append(matched_id)
        else:
            emerged_observed_ids.append(primitive_id)
        extension = LandscapeInferencePrimitiveExtension(
            authority="observed",
            classifier_id=BASIN_CLASSIFIER_ID,
            classifier_version=BASIN_CLASSIFIER_VERSION,
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
                node_ids=candidate.member_node_ids,
            ),
            matched_authored_primitive_id=matched_id,
            relationship_to_authored=relationship,
        )
        primitives.append(
            BasinSeedPrimitive(
                id=primitive_id,
                role=candidate.role,
                tags=["observed", "landscape_inference", candidate.capability_level],
                depth_hint=0,
                coherence_prior=candidate.basin_mass,
                stability_class=candidate.evidence_mode,
                extensions={
                    "landscape_inference": landscape_inference_primitive_mapping(extension),
                    "landscape_inference_basin": candidate.to_mapping(),
                },
            )
        )
    extensions = dict(load_result.inferred_seed.extensions)
    extensions["landscape_inference_basin_summary"] = canonicalize_json_value(
        {
            "classifier_id": BASIN_CLASSIFIER_ID,
            "classifier_version": BASIN_CLASSIFIER_VERSION,
            "runtime_family": load_result.source_runtime_family,
            "observed_basin_count": len(candidates),
            "preserved_authored_basin_ids": sorted(preserved_authored_ids),
            "emerged_observed_basin_ids": sorted(emerged_observed_ids),
            "dissolved_authored_basin_ids": sorted(
                set(authored_by_id) - set(preserved_authored_ids)
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


def classify_landscape_basin_candidates(
    substrate: LandscapeInferenceEvidenceSubstrate,
    *,
    runtime_family: str,
) -> tuple[LandscapeInferenceBasinCandidate, ...]:
    """Classify observed basin candidates from normalized checkpoint evidence."""

    if not substrate.checkpoint_graphs:
        return ()
    final_graph = substrate.checkpoint_graphs[-1]
    groups = _basin_groups(final_graph)
    candidates: list[LandscapeInferenceBasinCandidate] = []
    for basin_id, member_ids in sorted(groups.items(), key=lambda item: _sort_key(item[0])):
        representative = _representative_node(final_graph, basin_id, member_ids)
        if representative is None:
            continue
        node = final_graph.nodes[representative]
        if not _has_basin_evidence(node, member_ids):
            continue
        checkpoint_ids = _checkpoints_where_members_persist(substrate, member_ids)
        basin_mass, basin_mass_source = _candidate_basin_mass(final_graph, member_ids, node)
        evidence_mode, confidence, capability_level = _candidate_mode(
            runtime_family,
            node,
            basin_mass_source,
            len(member_ids),
        )
        role = "identity_basin" if node.sink_flag or len(member_ids) > 1 else "basin_seed"
        candidates.append(
            LandscapeInferenceBasinCandidate(
                basin_id=basin_id,
                representative_node_id=representative,
                member_node_ids=tuple(sorted(member_ids)),
                checkpoint_ids=checkpoint_ids,
                persistence_steps=len(checkpoint_ids),
                evidence_mode=evidence_mode,
                confidence=confidence,
                role=role,
                basin_mass=basin_mass,
                basin_mass_source=basin_mass_source,
                gradient_norm=node.gradient_norm,
                min_signed_hessian=node.min_signed_hessian,
                capability_level=capability_level,
                evidence_fields=_candidate_evidence_fields(runtime_family, node, basin_mass_source),
            )
        )
    return tuple(candidates)


def _basin_groups(graph: LandscapeInferenceCheckpointGraph) -> dict[str, tuple[int, ...]]:
    grouped: dict[str, set[int]] = defaultdict(set)
    for node_id, node in sorted(graph.nodes.items()):
        if node.basin_id is not None:
            grouped[str(node.basin_id)].add(node_id)
        elif node.sink_flag:
            grouped[str(node_id)].add(node_id)
    return {key: tuple(sorted(value)) for key, value in grouped.items()}


def _representative_node(
    graph: LandscapeInferenceCheckpointGraph,
    basin_id: str,
    member_ids: Sequence[int],
) -> int | None:
    for node_id in sorted(member_ids):
        node = graph.nodes[node_id]
        if node.sink_flag:
            return node_id
    try:
        basin_node_id = int(basin_id)
    except ValueError:
        basin_node_id = None
    if basin_node_id in member_ids:
        return basin_node_id
    return min(member_ids) if member_ids else None


def _has_basin_evidence(node: LandscapeInferenceNodeEvidence, member_ids: Sequence[int]) -> bool:
    return bool(
        node.sink_flag
        or node.basin_id is not None
        or node.basin_mass is not None
        or len(member_ids) > 1
    )


def _checkpoints_where_members_persist(
    substrate: LandscapeInferenceEvidenceSubstrate,
    member_ids: Sequence[int],
) -> tuple[str, ...]:
    members = set(int(item) for item in member_ids)
    return tuple(
        graph.checkpoint_id
        for graph in substrate.checkpoint_graphs
        if members <= set(graph.nodes)
    )


def _candidate_basin_mass(
    graph: LandscapeInferenceCheckpointGraph,
    member_ids: Sequence[int],
    representative: LandscapeInferenceNodeEvidence,
) -> tuple[float | None, str]:
    if representative.basin_mass is not None:
        return (representative.basin_mass, "checkpoint_basin_mass")
    coherence_values = [
        graph.nodes[node_id].coherence
        for node_id in member_ids
        if graph.nodes[node_id].coherence is not None
    ]
    if coherence_values:
        return (float(sum(coherence_values)), "coherence_mass_fallback")
    return (None, "unavailable")


def _candidate_mode(
    runtime_family: str,
    node: LandscapeInferenceNodeEvidence,
    basin_mass_source: str,
    member_count: int,
) -> tuple[str, float, str]:
    has_geometry = node.gradient_norm is not None and node.min_signed_hessian is not None
    has_true_mass = basin_mass_source == "checkpoint_basin_mass"
    if runtime_family in {"grcv3", "grc9v3"} and has_geometry and has_true_mass:
        return ("full_geometric_basin", 0.9 if node.sink_flag else 0.8, "full_geometric")
    if runtime_family in {"grcv3", "grc9v3"} and has_geometry:
        return ("geometric_basin_mass_proxy", 0.75 if node.sink_flag else 0.65, "geometric_mass_proxy")
    if runtime_family == "grc9":
        confidence = 0.65 if node.sink_flag or member_count > 1 else 0.5
        return ("topology_mechanical_basin", confidence, "topology_mechanical")
    return ("weak_basin_evidence", 0.45, "weak")


def _candidate_evidence_fields(
    runtime_family: str,
    node: LandscapeInferenceNodeEvidence,
    basin_mass_source: str,
) -> tuple[str, ...]:
    fields = ["graph_checkpoints.node_records.basin_id"]
    if node.sink_flag:
        fields.append("graph_checkpoints.node_records.sink_flag")
    if node.gradient_norm is not None:
        fields.append("graph_checkpoints.node_records.gradient_norm")
    if node.min_signed_hessian is not None:
        fields.append("graph_checkpoints.node_records.min_signed_hessian")
    if basin_mass_source == "checkpoint_basin_mass":
        fields.append("graph_checkpoints.node_records.basin_mass")
    elif basin_mass_source == "coherence_mass_fallback":
        fields.append("graph_checkpoints.node_records.coherence")
    fields.append(f"family_capability.{runtime_family}")
    return tuple(fields)


def _authored_basin_primitives_by_id(seed: LandscapeSeed | None) -> Mapping[str, LandscapePrimitive]:
    if seed is None:
        return {}
    return {
        primitive.id: primitive
        for primitive in seed.primitives
        if primitive.type == "basin"
    }


def _source_session_id_from_path(path: str | Path) -> str:
    for part in reversed(Path(path).parts):
        if part.startswith("S") and part[1:].isdigit():
            return part
    return Path(path).name


def _safe_id(value: str) -> str:
    return "".join(character if character.isalnum() or character == "_" else "_" for character in str(value))


def _sort_key(value: str) -> tuple[int, str]:
    try:
        return (0, f"{int(value):012d}")
    except ValueError:
        return (1, value)


__all__ = [
    "BASIN_CLASSIFIER_ID",
    "BASIN_CLASSIFIER_VERSION",
    "LandscapeInferenceBasinCandidate",
    "classify_landscape_basin_candidates",
    "infer_landscape_basin_seed",
]
