"""Observed valley/path classifier for landscape inference."""

from __future__ import annotations

from collections import defaultdict
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
    LandscapeInferencePathEvidence,
    build_landscape_inference_evidence_substrate,
    extract_landscape_inference_candidate_paths,
    summarize_landscape_inference_path_flux_stability,
    summarize_landscape_inference_path_persistence,
)
from .seed import BasinSeedPrimitive, LandscapePrimitive, LandscapeSeed, ValleySeedPrimitive


VALLEY_CLASSIFIER_ID = "landscape_inference_valley_classifier"
VALLEY_CLASSIFIER_VERSION = "landscape_inference_iter4_v1"
_MIN_EMIT_SIGNIFICANCE_SCORE = 0.08


@dataclass(frozen=True)
class LandscapeInferenceValleyCandidate:
    """Path-level candidate assembled from checkpoint evidence."""

    candidate_id: str
    from_basin_id: str
    to_basin_id: str
    from_node_id: int
    to_node_id: int
    path_node_ids: tuple[int, ...]
    path_edge_ids: tuple[int, ...]
    checkpoint_ids: tuple[str, ...]
    persistence_steps: int
    present_count: int
    ruptured_count: int
    missing_node_ids: tuple[int, ...]
    missing_edge_pairs: tuple[tuple[int, int], ...]
    bottleneck_conductance: float | None
    total_abs_flux: float | None
    mean_abs_flux: float | None
    total_geometric_length: float | None
    total_temporal_delay: float | None
    mean_flux_coupling: float | None
    bridge_edge_ids: tuple[int, ...]
    bridge_ambiguity_tier: str
    intermediate_basin_node_ids: tuple[int, ...]
    directionality: str
    flux_observed_steps: int
    flux_observed_fraction: float
    flux_stability_score: float
    flux_stability_mode: str
    status: str
    rejection_reason: str | None
    confidence: float
    evidence_fields: tuple[str, ...]
    significance_score: float
    significance_reason: str
    ranking_score: float
    ranking_reason: str
    deduplication_group_id: str
    emitted: bool = False

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "candidate_id": self.candidate_id,
                "from_basin_id": self.from_basin_id,
                "to_basin_id": self.to_basin_id,
                "from_node_id": self.from_node_id,
                "to_node_id": self.to_node_id,
                "path_node_ids": list(self.path_node_ids),
                "path_edge_ids": list(self.path_edge_ids),
                "checkpoint_ids": list(self.checkpoint_ids),
                "persistence_steps": self.persistence_steps,
                "present_count": self.present_count,
                "ruptured_count": self.ruptured_count,
                "missing_node_ids": list(self.missing_node_ids),
                "missing_edge_pairs": [list(pair) for pair in self.missing_edge_pairs],
                "bottleneck_conductance": self.bottleneck_conductance,
                "total_abs_flux": self.total_abs_flux,
                "mean_abs_flux": self.mean_abs_flux,
                "total_geometric_length": self.total_geometric_length,
                "total_temporal_delay": self.total_temporal_delay,
                "mean_flux_coupling": self.mean_flux_coupling,
                "bridge_edge_ids": list(self.bridge_edge_ids),
                "bridge_ambiguity_tier": self.bridge_ambiguity_tier,
                "intermediate_basin_node_ids": list(self.intermediate_basin_node_ids),
                "directionality": self.directionality,
                "flux_observed_steps": self.flux_observed_steps,
                "flux_observed_fraction": self.flux_observed_fraction,
                "flux_stability_score": self.flux_stability_score,
                "flux_stability_mode": self.flux_stability_mode,
                "status": self.status,
                "rejection_reason": self.rejection_reason,
                "confidence": self.confidence,
                "evidence_fields": list(self.evidence_fields),
                "significance_score": self.significance_score,
                "significance_reason": self.significance_reason,
                "ranking_score": self.ranking_score,
                "ranking_reason": self.ranking_reason,
                "deduplication_group_id": self.deduplication_group_id,
                "emitted": self.emitted,
            }
        )


def infer_landscape_valley_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    authored_seed: LandscapeSeed | None = None,
    max_valleys_per_endpoint_pair: int = 1,
) -> LandscapeSeed:
    """Return a normal `LandscapeSeed` with observed valley primitives added."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates = classify_landscape_valley_candidates(
        resolved_substrate,
        runtime_family=load_result.source_runtime_family,
    )
    emitted_candidates = select_emitted_landscape_valley_candidates(
        candidates,
        max_valleys_per_endpoint_pair=max_valleys_per_endpoint_pair,
    )
    emitted_candidate_ids = {candidate.candidate_id for candidate in emitted_candidates}
    authored_valleys = _authored_valley_primitives_by_endpoint(authored_seed)
    primitives: list[LandscapePrimitive] = list(load_result.inferred_seed.primitives)
    existing_ids = {primitive.id for primitive in primitives}
    emerged_ids: list[str] = []
    preserved_ids: list[str] = []
    for candidate in emitted_candidates:
        from_id = _basin_primitive_id(candidate.from_basin_id)
        to_id = _basin_primitive_id(candidate.to_basin_id)
        for basin_id, primitive_id in (
            (candidate.from_basin_id, from_id),
            (candidate.to_basin_id, to_id),
        ):
            if primitive_id not in existing_ids:
                primitives.append(
                    BasinSeedPrimitive(
                        id=primitive_id,
                        role="identity_basin_endpoint",
                        tags=["observed", "landscape_inference", "valley_endpoint"],
                        depth_hint=0,
                        stability_class="endpoint_reference",
                        extensions={
                            "landscape_inference_endpoint": {
                                "basin_id": basin_id,
                                "classifier_id": VALLEY_CLASSIFIER_ID,
                            }
                        },
                    )
                )
                existing_ids.add(primitive_id)
        primitive_id = f"observed_valley_{_safe_id(candidate.candidate_id)}"
        matched_id = authored_valleys.get((from_id, to_id))
        relationship = "preserved" if matched_id is not None else "emerged"
        if matched_id is None:
            emerged_ids.append(primitive_id)
        else:
            preserved_ids.append(matched_id)
        extension = LandscapeInferencePrimitiveExtension(
            authority="observed",
            classifier_id=VALLEY_CLASSIFIER_ID,
            classifier_version=VALLEY_CLASSIFIER_VERSION,
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
                node_ids=(candidate.from_node_id, candidate.to_node_id),
                edge_ids=candidate.path_edge_ids,
                path_node_ids=candidate.path_node_ids,
            ),
            matched_authored_primitive_id=matched_id,
            relationship_to_authored=relationship,
        )
        primitives.append(
            ValleySeedPrimitive(
                id=primitive_id,
                role="valley_channel",
                tags=["observed", "landscape_inference", "path_evidence"],
                from_id=from_id,
                to_id=to_id,
                path_hint="checkpoint_path",
                coherence_prior=candidate.mean_abs_flux,
                channel_role="valley_channel",
                extensions={
                    "landscape_inference": landscape_inference_primitive_mapping(extension),
                    "landscape_inference_valley": candidate.to_mapping(),
                },
            )
        )
    extensions = dict(load_result.inferred_seed.extensions)
    extensions["landscape_inference_valley_summary"] = canonicalize_json_value(
        {
            "classifier_id": VALLEY_CLASSIFIER_ID,
            "classifier_version": VALLEY_CLASSIFIER_VERSION,
            "runtime_family": load_result.source_runtime_family,
            "candidate_count": len(candidates),
            "raw_accepted_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "accepted"
            ),
            "observed_valley_count": len(emitted_candidates),
            "preserved_authored_valley_ids": sorted(preserved_ids),
            "emerged_observed_valley_ids": sorted(emerged_ids),
            "rejected_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "rejected"
            ),
            "ambiguous_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "ambiguous"
            ),
            "max_valleys_per_endpoint_pair": max_valleys_per_endpoint_pair,
            "deduplicated_candidate_count": sum(
                1
                for candidate in candidates
                if candidate.status == "accepted"
                and candidate.candidate_id not in emitted_candidate_ids
            ),
            "significance_filtered_candidate_count": sum(
                1
                for candidate in candidates
                if candidate.status == "accepted"
                and candidate.significance_score < _MIN_EMIT_SIGNIFICANCE_SCORE
            ),
            "bridge_ambiguity_counts": dict(
                sorted(
                    (tier, sum(1 for candidate in candidates if candidate.bridge_ambiguity_tier == tier))
                    for tier in {candidate.bridge_ambiguity_tier for candidate in candidates}
                )
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


def classify_landscape_valley_candidates(
    substrate: LandscapeInferenceEvidenceSubstrate,
    *,
    runtime_family: str,
    max_paths_per_pair: int = 8,
) -> tuple[LandscapeInferenceValleyCandidate, ...]:
    """Classify observed valley/path candidates from normalized checkpoint evidence."""

    del runtime_family
    if not substrate.checkpoint_graphs:
        return ()
    final_graph = substrate.checkpoint_graphs[-1]
    basin_groups = _basin_groups(final_graph)
    candidates: list[LandscapeInferenceValleyCandidate] = []
    for from_basin, to_basin in _basin_pairs(basin_groups):
        paths = extract_landscape_inference_candidate_paths(
            final_graph,
            basin_groups[from_basin],
            basin_groups[to_basin],
            max_paths=max_paths_per_pair,
            max_depth=max(1, len(final_graph.nodes) - 1),
            include_bridge_paths=True,
        )
        for path in paths:
            candidates.append(
                _candidate_from_path(
                    substrate,
                    final_graph,
                    path,
                    from_basin_id=from_basin,
                    to_basin_id=to_basin,
                )
            )
    return tuple(sorted(candidates, key=lambda candidate: candidate.candidate_id))


def select_emitted_landscape_valley_candidates(
    candidates: Sequence[LandscapeInferenceValleyCandidate],
    *,
    max_valleys_per_endpoint_pair: int = 1,
) -> tuple[LandscapeInferenceValleyCandidate, ...]:
    """Return ranked, endpoint-deduplicated candidates for seed emission."""

    if max_valleys_per_endpoint_pair <= 0:
        return ()
    grouped: dict[str, list[LandscapeInferenceValleyCandidate]] = defaultdict(list)
    for candidate in candidates:
        if candidate.status == "accepted":
            grouped[candidate.deduplication_group_id].append(candidate)
    selected: list[LandscapeInferenceValleyCandidate] = []
    for group_id in sorted(grouped):
        significant = tuple(
            candidate
            for candidate in grouped[group_id]
            if candidate.significance_score >= _MIN_EMIT_SIGNIFICANCE_SCORE
        )
        ranked = sorted(significant or grouped[group_id], key=_candidate_sort_key)
        for candidate in ranked[:max_valleys_per_endpoint_pair]:
            selected.append(_candidate_with_emitted(candidate))
    return tuple(sorted(selected, key=lambda candidate: candidate.candidate_id))


def _candidate_from_path(
    substrate: LandscapeInferenceEvidenceSubstrate,
    final_graph: LandscapeInferenceCheckpointGraph,
    path: LandscapeInferencePathEvidence,
    *,
    from_basin_id: str,
    to_basin_id: str,
) -> LandscapeInferenceValleyCandidate:
    persistence = summarize_landscape_inference_path_persistence(substrate, path.node_ids)
    flux_stability = summarize_landscape_inference_path_flux_stability(substrate, path.node_ids)
    edges = tuple(final_graph.edges[edge_id] for edge_id in path.edge_ids)
    bridge_tier = _bridge_ambiguity_tier(path)
    intermediate_basin_nodes = _intermediate_stable_basin_nodes(
        final_graph,
        path.node_ids,
        allowed_basin_ids={from_basin_id, to_basin_id},
    )
    status, reason, confidence = _valley_status(
        path,
        persistence,
        intermediate_basin_nodes,
        diagnostic_only=substrate.diagnostic_only,
    )
    candidate_id = (
        f"{_safe_id(from_basin_id)}_to_{_safe_id(to_basin_id)}_"
        f"{'_'.join(str(node_id) for node_id in path.node_ids)}"
    )
    significance_score, significance_reason = _candidate_significance(
        final_graph,
        path,
        flux_stability_score=flux_stability.stability_score,
    )
    ranking_score, ranking_reason = _candidate_ranking(
        path,
        persistence,
        status,
        significance_score=significance_score,
        flux_stability_score=flux_stability.stability_score,
    )
    deduplication_group_id = _deduplication_group_id(from_basin_id, to_basin_id)
    return LandscapeInferenceValleyCandidate(
        candidate_id=candidate_id,
        from_basin_id=from_basin_id,
        to_basin_id=to_basin_id,
        from_node_id=path.node_ids[0],
        to_node_id=path.node_ids[-1],
        path_node_ids=path.node_ids,
        path_edge_ids=path.edge_ids,
        checkpoint_ids=tuple(graph.checkpoint_id for graph in substrate.checkpoint_graphs),
        persistence_steps=persistence.present_count,
        present_count=persistence.present_count,
        ruptured_count=persistence.ruptured_count,
        missing_node_ids=persistence.missing_node_ids,
        missing_edge_pairs=persistence.missing_edge_pairs,
        bottleneck_conductance=path.bottleneck_conductance,
        total_abs_flux=path.total_abs_flux,
        mean_abs_flux=path.mean_abs_flux,
        total_geometric_length=_sum_optional(edge.geometric_length for edge in edges),
        total_temporal_delay=_sum_optional(edge.temporal_delay for edge in edges),
        mean_flux_coupling=_mean_optional(edge.flux_coupling for edge in edges),
        bridge_edge_ids=path.bridge_edge_ids,
        bridge_ambiguity_tier=bridge_tier,
        intermediate_basin_node_ids=intermediate_basin_nodes,
        directionality=path.directionality,
        flux_observed_steps=flux_stability.observed_count,
        flux_observed_fraction=flux_stability.observed_fraction,
        flux_stability_score=flux_stability.stability_score,
        flux_stability_mode=flux_stability.stability_mode,
        status=status,
        rejection_reason=reason,
        confidence=confidence,
        evidence_fields=_valley_evidence_fields(path, edges, persistence, flux_stability),
        significance_score=significance_score,
        significance_reason=significance_reason,
        ranking_score=ranking_score,
        ranking_reason=ranking_reason,
        deduplication_group_id=deduplication_group_id,
    )


def _valley_status(
    path: LandscapeInferencePathEvidence,
    persistence: Any,
    intermediate_basin_nodes: Sequence[int],
    *,
    diagnostic_only: bool,
) -> tuple[str, str | None, float]:
    if path.bridge_edge_ids and len(path.bridge_edge_ids) == len(path.edge_ids):
        return ("rejected", "bridge_only_path", 0.0)
    if path.bridge_edge_ids:
        return ("ambiguous", "contains_lowering_bridge_edge", 0.35)
    if persistence.ruptured_count:
        return ("rejected", "path_ruptured_across_window", 0.0)
    if intermediate_basin_nodes:
        return ("rejected", "stable_basin_interior_on_path", 0.0)
    if path.total_abs_flux is None or path.total_abs_flux <= 0.0:
        return ("rejected", "missing_positive_flux_support", 0.0)
    if diagnostic_only:
        return ("ambiguous", "short_persistence_window", 0.45)
    return ("accepted", None, 0.78)


def _bridge_ambiguity_tier(path: LandscapeInferencePathEvidence) -> str:
    if not path.bridge_edge_ids:
        return "none"
    bridge_edge_ids = set(path.bridge_edge_ids)
    if len(bridge_edge_ids) == len(path.edge_ids):
        return "bridge_only"
    bridge_positions = {
        index for index, edge_id in enumerate(path.edge_ids) if edge_id in bridge_edge_ids
    }
    endpoint_positions = {0, max(0, len(path.edge_ids) - 1)}
    at_endpoint = any(position in endpoint_positions for position in bridge_positions)
    in_middle = any(position not in endpoint_positions for position in bridge_positions)
    if at_endpoint and in_middle:
        return "bridge_mixed"
    if at_endpoint:
        return "bridge_at_endpoint"
    return "bridge_in_middle"


def _candidate_significance(
    graph: LandscapeInferenceCheckpointGraph,
    path: LandscapeInferencePathEvidence,
    *,
    flux_stability_score: float,
) -> tuple[float, str]:
    endpoint_score = _endpoint_significance(graph, path.node_ids[0])
    endpoint_score += _endpoint_significance(graph, path.node_ids[-1])
    endpoint_score /= 2.0
    score = (
        _bounded_metric(path.total_abs_flux) * 0.35
        + _bounded_metric(path.bottleneck_conductance) * 0.2
        + flux_stability_score * 0.3
        + endpoint_score * 0.15
    )
    return (
        float(max(0.0, min(1.0, score))),
        "flux_support>bottleneck_conductance>flux_stability>endpoint_role",
    )


def _endpoint_significance(graph: LandscapeInferenceCheckpointGraph, node_id: int) -> float:
    node = graph.nodes.get(int(node_id))
    if node is None:
        return 0.0
    score = 0.15
    if node.sink_flag:
        score += 0.35
    if node.basin_mass is not None and node.basin_mass > 0.0:
        score += min(0.35, _bounded_metric(float(node.basin_mass)) * 0.35)
    if node.provenance:
        score += 0.15
    return float(max(0.0, min(1.0, score)))


def _candidate_ranking(
    path: LandscapeInferencePathEvidence,
    persistence: Any,
    status: str,
    *,
    significance_score: float,
    flux_stability_score: float,
) -> tuple[float, str]:
    status_score = {"accepted": 3.0, "ambiguous": 1.0, "rejected": 0.0}.get(status, 0.0)
    non_bridge_score = 1.0 if not path.bridge_edge_ids else 0.0
    persistence_score = float(getattr(persistence, "present_count", 0))
    flux_score = _bounded_metric(path.total_abs_flux)
    bottleneck_score = _bounded_metric(path.bottleneck_conductance)
    path_length_penalty = 1.0 / max(1, len(path.edge_ids))
    score = (
        status_score * 1_000_000.0
        + non_bridge_score * 100_000.0
        + significance_score * 10_000.0
        + persistence_score * 1_000.0
        + flux_stability_score * 500.0
        + flux_score * 100.0
        + bottleneck_score * 10.0
        + path_length_penalty
    )
    return (
        float(score),
        (
            "status>non_bridge>significance>persistence>"
            "flux_stability>flux_support>"
            "bottleneck_conductance>shorter_path"
        ),
    )


def _candidate_sort_key(
    candidate: LandscapeInferenceValleyCandidate,
) -> tuple[float, int, str]:
    return (-candidate.ranking_score, len(candidate.path_edge_ids), candidate.candidate_id)


def _candidate_with_emitted(
    candidate: LandscapeInferenceValleyCandidate,
) -> LandscapeInferenceValleyCandidate:
    return LandscapeInferenceValleyCandidate(
        candidate_id=candidate.candidate_id,
        from_basin_id=candidate.from_basin_id,
        to_basin_id=candidate.to_basin_id,
        from_node_id=candidate.from_node_id,
        to_node_id=candidate.to_node_id,
        path_node_ids=candidate.path_node_ids,
        path_edge_ids=candidate.path_edge_ids,
        checkpoint_ids=candidate.checkpoint_ids,
        persistence_steps=candidate.persistence_steps,
        present_count=candidate.present_count,
        ruptured_count=candidate.ruptured_count,
        missing_node_ids=candidate.missing_node_ids,
        missing_edge_pairs=candidate.missing_edge_pairs,
        bottleneck_conductance=candidate.bottleneck_conductance,
        total_abs_flux=candidate.total_abs_flux,
        mean_abs_flux=candidate.mean_abs_flux,
        total_geometric_length=candidate.total_geometric_length,
        total_temporal_delay=candidate.total_temporal_delay,
        mean_flux_coupling=candidate.mean_flux_coupling,
        bridge_edge_ids=candidate.bridge_edge_ids,
        bridge_ambiguity_tier=candidate.bridge_ambiguity_tier,
        intermediate_basin_node_ids=candidate.intermediate_basin_node_ids,
        directionality=candidate.directionality,
        flux_observed_steps=candidate.flux_observed_steps,
        flux_observed_fraction=candidate.flux_observed_fraction,
        flux_stability_score=candidate.flux_stability_score,
        flux_stability_mode=candidate.flux_stability_mode,
        status=candidate.status,
        rejection_reason=candidate.rejection_reason,
        confidence=candidate.confidence,
        evidence_fields=candidate.evidence_fields,
        significance_score=candidate.significance_score,
        significance_reason=candidate.significance_reason,
        ranking_score=candidate.ranking_score,
        ranking_reason=candidate.ranking_reason,
        deduplication_group_id=candidate.deduplication_group_id,
        emitted=True,
    )


def _bounded_metric(value: float | None) -> float:
    if value is None or value <= 0.0:
        return 0.0
    return float(value / (1.0 + value))


def _deduplication_group_id(from_basin_id: str, to_basin_id: str) -> str:
    left, right = sorted((_safe_id(from_basin_id), _safe_id(to_basin_id)))
    return f"{left}__{right}"


def _basin_groups(graph: LandscapeInferenceCheckpointGraph) -> dict[str, tuple[int, ...]]:
    grouped: dict[str, set[int]] = defaultdict(set)
    for node_id, node in sorted(graph.nodes.items()):
        if node.basin_id is not None:
            grouped[str(node.basin_id)].add(node_id)
        elif node.sink_flag:
            grouped[str(node_id)].add(node_id)
    return {basin_id: tuple(sorted(nodes)) for basin_id, nodes in grouped.items()}


def _basin_pairs(groups: Mapping[str, Sequence[int]]) -> tuple[tuple[str, str], ...]:
    basin_ids = tuple(sorted(groups, key=_sort_key))
    return tuple(
        (basin_ids[index], basin_ids[inner_index])
        for index in range(len(basin_ids))
        for inner_index in range(index + 1, len(basin_ids))
    )


def _intermediate_stable_basin_nodes(
    graph: LandscapeInferenceCheckpointGraph,
    path_node_ids: Sequence[int],
    *,
    allowed_basin_ids: set[str],
) -> tuple[int, ...]:
    interior = path_node_ids[1:-1]
    rejected: list[int] = []
    for node_id in interior:
        node = graph.nodes[node_id]
        basin_id = None if node.basin_id is None else str(node.basin_id)
        if node.sink_flag or (basin_id is not None and basin_id not in allowed_basin_ids):
            rejected.append(node_id)
    return tuple(sorted(rejected))


def _valley_evidence_fields(
    path: LandscapeInferencePathEvidence,
    edges: Sequence[Any],
    persistence: Any,
    flux_stability: Any,
) -> tuple[str, ...]:
    fields = [
        "graph_checkpoints.edge_records.edge_id",
        "graph_checkpoints.edge_records.signed_flux",
        "graph_checkpoints.edge_records.conductance",
        "graph_checkpoints.node_records.basin_id",
        "graph_checkpoints.path_persistence.present_count",
        "graph_checkpoints.path_flux_stability.stability_score",
    ]
    if getattr(flux_stability, "observed_count", 0):
        fields.append("graph_checkpoints.path_flux_stability.flux_series")
    if any(edge.geometric_length is not None for edge in edges):
        fields.append("graph_checkpoints.edge_records.geometric_length")
    if any(edge.temporal_delay is not None for edge in edges):
        fields.append("graph_checkpoints.edge_records.temporal_delay")
    if any(edge.flux_coupling is not None for edge in edges):
        fields.append("graph_checkpoints.edge_records.flux_coupling")
    if path.bridge_edge_ids:
        fields.append("graph_checkpoints.edge_records.grcl9_edge_kind")
    if persistence.ruptured_count:
        fields.append("graph_checkpoints.path_persistence.ruptured_count")
    return tuple(fields)


def _authored_valley_primitives_by_endpoint(
    authored_seed: LandscapeSeed | None,
) -> dict[tuple[str | None, str | None], str]:
    if authored_seed is None:
        return {}
    result: dict[tuple[str | None, str | None], str] = {}
    for primitive in authored_seed.primitives:
        if isinstance(primitive, ValleySeedPrimitive):
            result[(primitive.from_id, primitive.to_id)] = primitive.id
    return result


def _basin_primitive_id(basin_id: str) -> str:
    return f"observed_basin_{_safe_id(basin_id)}"


def _safe_id(value: object) -> str:
    text = str(value).strip().lower().replace("-", "_")
    return "".join(char if char.isalnum() or char == "_" else "_" for char in text).strip("_") or "unknown"


def _sort_key(value: str) -> tuple[int, int | str]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)


def _sum_optional(values: Sequence[float | None]) -> float | None:
    finite = tuple(float(value) for value in values if value is not None)
    return None if not finite else float(sum(finite))


def _mean_optional(values: Sequence[float | None]) -> float | None:
    finite = tuple(float(value) for value in values if value is not None)
    return None if not finite else float(sum(finite) / len(finite))


__all__ = [
    "LandscapeInferenceValleyCandidate",
    "VALLEY_CLASSIFIER_ID",
    "VALLEY_CLASSIFIER_VERSION",
    "classify_landscape_valley_candidates",
    "infer_landscape_valley_seed",
    "select_emitted_landscape_valley_candidates",
]
