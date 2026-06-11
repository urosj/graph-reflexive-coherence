"""Observed pheromone/path-memory classifier for landscape inference."""

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


PHEROMONE_CLASSIFIER_ID = "landscape_inference_pheromone_classifier"
PHEROMONE_CLASSIFIER_VERSION = "landscape_inference_iter7_v1"

_EMPHASIS_EVENT_KINDS = frozenset(("choice_detected", "collapse"))


@dataclass(frozen=True)
class LandscapeInferencePheromoneCandidate:
    """Observed path-memory candidate assembled from repeated path activity."""

    candidate_id: str
    from_basin_id: str
    to_basin_id: str
    from_node_id: int
    to_node_id: int
    path_node_ids: tuple[int, ...]
    path_edge_ids: tuple[int, ...]
    checkpoint_ids: tuple[str, ...]
    checkpoint_count: int
    persistence_steps: int
    flux_observed_steps: int
    flux_series: tuple[float | None, ...]
    flux_observed_fraction: float
    flux_stability_score: float
    flux_stability_mode: str
    mean_abs_flux: float | None
    max_abs_flux: float | None
    bottleneck_conductance_first: float | None
    bottleneck_conductance_last: float | None
    conductance_reinforced: bool
    emphasis_event_refs: tuple[str, ...]
    bridge_edge_ids: tuple[int, ...]
    intermediate_basin_node_ids: tuple[int, ...]
    status: str
    rejection_reason: str | None
    confidence: float
    promotion_candidate_status: str
    policy_suggestions: tuple[str, ...]
    evidence_fields: tuple[str, ...]

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
                "checkpoint_count": self.checkpoint_count,
                "persistence_steps": self.persistence_steps,
                "flux_observed_steps": self.flux_observed_steps,
                "flux_series": list(self.flux_series),
                "flux_observed_fraction": self.flux_observed_fraction,
                "flux_stability_score": self.flux_stability_score,
                "flux_stability_mode": self.flux_stability_mode,
                "mean_abs_flux": self.mean_abs_flux,
                "max_abs_flux": self.max_abs_flux,
                "bottleneck_conductance_first": self.bottleneck_conductance_first,
                "bottleneck_conductance_last": self.bottleneck_conductance_last,
                "conductance_reinforced": self.conductance_reinforced,
                "emphasis_event_refs": list(self.emphasis_event_refs),
                "bridge_edge_ids": list(self.bridge_edge_ids),
                "intermediate_basin_node_ids": list(self.intermediate_basin_node_ids),
                "status": self.status,
                "rejection_reason": self.rejection_reason,
                "confidence": self.confidence,
                "promotion_candidate_status": self.promotion_candidate_status,
                "policy_suggestions": list(self.policy_suggestions),
                "evidence_fields": list(self.evidence_fields),
            }
        )


def infer_landscape_pheromone_seed(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    max_markers_per_endpoint_pair: int = 1,
) -> LandscapeSeed:
    """Return a normal `LandscapeSeed` with observed pheromone markers added."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    candidates = classify_landscape_pheromone_candidates(
        load_result,
        substrate=resolved_substrate,
    )
    emitted = select_emitted_landscape_pheromone_candidates(
        candidates,
        max_markers_per_endpoint_pair=max_markers_per_endpoint_pair,
    )
    primitives: list[LandscapePrimitive] = list(load_result.inferred_seed.primitives)
    existing_ids = {primitive.id for primitive in primitives}
    emerged_ids: list[str] = []
    for candidate in emitted:
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
                        tags=["observed", "landscape_inference", "pheromone_endpoint"],
                        depth_hint=0,
                        stability_class="endpoint_reference",
                        extensions={
                            "landscape_inference_endpoint": {
                                "basin_id": basin_id,
                                "classifier_id": PHEROMONE_CLASSIFIER_ID,
                            }
                        },
                    )
                )
                existing_ids.add(primitive_id)
        primitive_id = f"observed_pheromone_{_safe_id(candidate.candidate_id)}"
        emerged_ids.append(primitive_id)
        extension = LandscapeInferencePrimitiveExtension(
            authority="observed",
            classifier_id=PHEROMONE_CLASSIFIER_ID,
            classifier_version=PHEROMONE_CLASSIFIER_VERSION,
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
            matched_authored_primitive_id=None,
            relationship_to_authored="emerged",
        )
        primitives.append(
            ValleySeedPrimitive(
                id=primitive_id,
                role="pheromone_marker",
                tags=["observed", "landscape_inference", "path_memory"],
                from_id=from_id,
                to_id=to_id,
                path_hint="checkpoint_path_memory",
                coherence_prior=candidate.mean_abs_flux,
                channel_role="pheromone_marker",
                extensions={
                    "landscape_inference": landscape_inference_primitive_mapping(extension),
                    "landscape_inference_pheromone": candidate.to_mapping(),
                },
            )
        )
    extensions = dict(load_result.inferred_seed.extensions)
    extensions["landscape_inference_pheromone_summary"] = canonicalize_json_value(
        {
            "classifier_id": PHEROMONE_CLASSIFIER_ID,
            "classifier_version": PHEROMONE_CLASSIFIER_VERSION,
            "runtime_family": load_result.source_runtime_family,
            "candidate_count": len(candidates),
            "accepted_candidate_count": sum(
                1 for candidate in candidates if candidate.status == "accepted"
            ),
            "observed_pheromone_count": len(emitted),
            "emerged_observed_pheromone_ids": sorted(emerged_ids),
            "promotion_policy_suggestion_count": sum(
                len(candidate.policy_suggestions) for candidate in emitted
            ),
            "identity_claim_count": 0,
            "max_markers_per_endpoint_pair": max_markers_per_endpoint_pair,
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


def classify_landscape_pheromone_candidates(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    max_paths_per_pair: int = 8,
    min_flux_observed_steps: int = 3,
    min_flux_observed_fraction: float = 0.6,
) -> tuple[LandscapeInferencePheromoneCandidate, ...]:
    """Classify path-memory candidates from repeated checkpoint path activity."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    if not resolved_substrate.checkpoint_graphs:
        return ()
    final_graph = resolved_substrate.checkpoint_graphs[-1]
    basin_groups = _basin_groups(final_graph)
    candidates: list[LandscapeInferencePheromoneCandidate] = []
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
                    load_result,
                    resolved_substrate,
                    final_graph,
                    path,
                    from_basin_id=from_basin,
                    to_basin_id=to_basin,
                    min_flux_observed_steps=min_flux_observed_steps,
                    min_flux_observed_fraction=min_flux_observed_fraction,
                )
            )
    return tuple(sorted(candidates, key=lambda candidate: candidate.candidate_id))


def select_emitted_landscape_pheromone_candidates(
    candidates: Sequence[LandscapeInferencePheromoneCandidate],
    *,
    max_markers_per_endpoint_pair: int = 1,
) -> tuple[LandscapeInferencePheromoneCandidate, ...]:
    """Return ranked accepted pheromone candidates for seed emission."""

    if max_markers_per_endpoint_pair <= 0:
        return ()
    grouped: dict[str, list[LandscapeInferencePheromoneCandidate]] = defaultdict(list)
    for candidate in candidates:
        if candidate.status == "accepted":
            grouped[_deduplication_group_id(candidate.from_basin_id, candidate.to_basin_id)].append(
                candidate
            )
    selected: list[LandscapeInferencePheromoneCandidate] = []
    for group_id in sorted(grouped):
        ranked = sorted(grouped[group_id], key=_candidate_sort_key)
        selected.extend(ranked[:max_markers_per_endpoint_pair])
    return tuple(sorted(selected, key=lambda candidate: candidate.candidate_id))


def _candidate_from_path(
    load_result: LandscapeInferenceArtifactLoadResult,
    substrate: LandscapeInferenceEvidenceSubstrate,
    final_graph: LandscapeInferenceCheckpointGraph,
    path: LandscapeInferencePathEvidence,
    *,
    from_basin_id: str,
    to_basin_id: str,
    min_flux_observed_steps: int,
    min_flux_observed_fraction: float,
) -> LandscapeInferencePheromoneCandidate:
    persistence = summarize_landscape_inference_path_persistence(substrate, path.node_ids)
    flux_stability = summarize_landscape_inference_path_flux_stability(substrate, path.node_ids)
    finite_flux = tuple(
        value for value in flux_stability.flux_series if value is not None and value > 0.0
    )
    flux_observed_steps = flux_stability.observed_count
    bottleneck_first = _path_bottleneck_conductance(substrate.checkpoint_graphs[0], path.node_ids)
    bottleneck_last = _path_bottleneck_conductance(final_graph, path.node_ids)
    conductance_reinforced = (
        bottleneck_first is not None
        and bottleneck_last is not None
        and bottleneck_last > bottleneck_first + 1e-12
    )
    intermediate_basin_nodes = _intermediate_stable_basin_nodes(
        final_graph,
        path.node_ids,
        allowed_basin_ids={from_basin_id, to_basin_id},
    )
    emphasis_event_refs = _emphasis_event_refs(load_result, path.node_ids)
    status, reason, confidence, promotion_status, suggestions = _pheromone_status(
        path,
        checkpoint_count=len(substrate.checkpoint_graphs),
        persistence_steps=persistence.present_count,
        flux_observed_steps=flux_observed_steps,
        flux_stability_score=flux_stability.stability_score,
        min_flux_observed_steps=min_flux_observed_steps,
        min_flux_observed_fraction=min_flux_observed_fraction,
        conductance_reinforced=conductance_reinforced,
        emphasis_event_refs=emphasis_event_refs,
        intermediate_basin_nodes=intermediate_basin_nodes,
        diagnostic_only=substrate.diagnostic_only,
    )
    candidate_id = (
        f"{_safe_id(from_basin_id)}_to_{_safe_id(to_basin_id)}_"
        f"{'_'.join(str(node_id) for node_id in path.node_ids)}"
    )
    return LandscapeInferencePheromoneCandidate(
        candidate_id=candidate_id,
        from_basin_id=from_basin_id,
        to_basin_id=to_basin_id,
        from_node_id=path.node_ids[0],
        to_node_id=path.node_ids[-1],
        path_node_ids=path.node_ids,
        path_edge_ids=path.edge_ids,
        checkpoint_ids=tuple(graph.checkpoint_id for graph in substrate.checkpoint_graphs),
        checkpoint_count=len(substrate.checkpoint_graphs),
        persistence_steps=persistence.present_count,
        flux_observed_steps=flux_observed_steps,
        flux_series=flux_stability.flux_series,
        flux_observed_fraction=flux_stability.observed_fraction,
        flux_stability_score=flux_stability.stability_score,
        flux_stability_mode=flux_stability.stability_mode,
        mean_abs_flux=None if not finite_flux else float(sum(finite_flux) / len(finite_flux)),
        max_abs_flux=None if not finite_flux else float(max(finite_flux)),
        bottleneck_conductance_first=bottleneck_first,
        bottleneck_conductance_last=bottleneck_last,
        conductance_reinforced=conductance_reinforced,
        emphasis_event_refs=emphasis_event_refs,
        bridge_edge_ids=path.bridge_edge_ids,
        intermediate_basin_node_ids=intermediate_basin_nodes,
        status=status,
        rejection_reason=reason,
        confidence=confidence,
        promotion_candidate_status=promotion_status,
        policy_suggestions=suggestions,
        evidence_fields=_pheromone_evidence_fields(
            path,
            flux_observed_steps=flux_observed_steps,
            flux_stability_score=flux_stability.stability_score,
            conductance_reinforced=conductance_reinforced,
            emphasis_event_refs=emphasis_event_refs,
        ),
    )


def _pheromone_status(
    path: LandscapeInferencePathEvidence,
    *,
    checkpoint_count: int,
    persistence_steps: int,
    flux_observed_steps: int,
    flux_stability_score: float,
    min_flux_observed_steps: int,
    min_flux_observed_fraction: float,
    conductance_reinforced: bool,
    emphasis_event_refs: Sequence[str],
    intermediate_basin_nodes: Sequence[int],
    diagnostic_only: bool,
) -> tuple[str, str | None, float, str, tuple[str, ...]]:
    if path.bridge_edge_ids and len(path.bridge_edge_ids) == len(path.edge_ids):
        return ("rejected", "bridge_only_path", 0.0, "not_considered", ())
    if persistence_steps < checkpoint_count:
        return ("rejected", "path_ruptured_across_window", 0.0, "not_considered", ())
    if intermediate_basin_nodes:
        return ("rejected", "stable_identity_basin_on_path", 0.0, "not_considered", ())
    required_steps = max(
        min_flux_observed_steps,
        int((checkpoint_count * min_flux_observed_fraction) + 0.999999),
    )
    repeated_flux = flux_observed_steps >= required_steps
    if not repeated_flux and not conductance_reinforced:
        if emphasis_event_refs:
            return (
                "ambiguous",
                "event_emphasis_without_repeated_path_activity",
                0.42,
                "policy_suggestion_only",
                ("monitor_collapse_emphasis_path_memory",),
            )
        return ("rejected", "missing_repeated_flux_or_reinforcement", 0.0, "not_considered", ())
    confidence = 0.7
    if repeated_flux:
        confidence += 0.08
    confidence += min(0.08, flux_stability_score * 0.08)
    if conductance_reinforced:
        confidence += 0.08
    if emphasis_event_refs:
        confidence += 0.04
    if diagnostic_only:
        confidence -= 0.2
    suggestions = ("consider_promote_pheromone_candidate",) if repeated_flux else ()
    return (
        "ambiguous" if diagnostic_only else "accepted",
        "short_persistence_window" if diagnostic_only else None,
        max(0.0, min(1.0, confidence)),
        "promotion_candidate" if suggestions else "observed_memory_only",
        suggestions,
    )


def _path_flux_series(
    substrate: LandscapeInferenceEvidenceSubstrate,
    node_ids: Sequence[int],
) -> tuple[float | None, ...]:
    return tuple(_path_total_abs_flux(graph, node_ids) for graph in substrate.checkpoint_graphs)


def _path_total_abs_flux(
    graph: LandscapeInferenceCheckpointGraph,
    node_ids: Sequence[int],
) -> float | None:
    values: list[float] = []
    for source, target in zip(node_ids, node_ids[1:]):
        edge_id = graph.edge_id_by_pair.get(_pair_key(source, target))
        if edge_id is None:
            return None
        signed_flux = graph.edges[edge_id].signed_flux
        if signed_flux is None:
            return None
        values.append(abs(float(signed_flux)))
    return float(sum(values))


def _path_bottleneck_conductance(
    graph: LandscapeInferenceCheckpointGraph,
    node_ids: Sequence[int],
) -> float | None:
    values: list[float] = []
    for source, target in zip(node_ids, node_ids[1:]):
        edge_id = graph.edge_id_by_pair.get(_pair_key(source, target))
        if edge_id is None:
            return None
        conductance = graph.edges[edge_id].conductance
        if conductance is None:
            return None
        values.append(float(conductance))
    return None if not values else float(min(values))


def _emphasis_event_refs(
    load_result: LandscapeInferenceArtifactLoadResult,
    node_ids: Sequence[int],
) -> tuple[str, ...]:
    path_nodes = set(int(item) for item in node_ids)
    refs: list[str] = []
    for row in load_result.telemetry_pack.event_rows:
        if str(row.event_kind) not in _EMPHASIS_EVENT_KINDS:
            continue
        node_id = _primary_node_id(row)
        if node_id in path_nodes:
            refs.append(f"step_{int(row.step_index)}:event_{int(row.event_index)}:{row.event_kind}")
    return tuple(refs)


def _primary_node_id(row: Any) -> int | None:
    family_extensions = _mapping(row.family_extensions)
    for family in family_extensions.values():
        mapping = _mapping(family)
        value = _optional_int(mapping.get("primary_node_id"))
        if value is not None:
            return value
        nested = _mapping(mapping.get("choice_collapse_evidence"))
        value = _optional_int(nested.get("node_id"))
        if value is not None:
            return value
    payload = _mapping(row.payload)
    for key in ("primary_node_id", "node_id", "candidate_node_id", "sink_node_id"):
        value = _optional_int(payload.get(key))
        if value is not None:
            return value
    return None


def _pheromone_evidence_fields(
    path: LandscapeInferencePathEvidence,
    *,
    flux_observed_steps: int,
    flux_stability_score: float,
    conductance_reinforced: bool,
    emphasis_event_refs: Sequence[str],
) -> tuple[str, ...]:
    fields = [
        "graph_checkpoints.edge_records.edge_id",
        "graph_checkpoints.edge_records.signed_flux",
        "graph_checkpoints.path_memory.flux_observed_steps",
        "graph_checkpoints.path_persistence.present_count",
        "graph_checkpoints.path_flux_stability.stability_score",
    ]
    if flux_stability_score > 0.0:
        fields.append("graph_checkpoints.path_flux_stability.stability_mode")
    if conductance_reinforced:
        fields.append("graph_checkpoints.edge_records.conductance")
    if emphasis_event_refs:
        fields.append("events.event_kind")
    if path.bridge_edge_ids:
        fields.append("graph_checkpoints.edge_records.grcl9_edge_kind")
    if flux_observed_steps:
        fields.append("graph_checkpoints.path_memory.flux_series")
    return tuple(fields)


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
    rejected: list[int] = []
    for node_id in path_node_ids[1:-1]:
        node = graph.nodes[node_id]
        basin_id = None if node.basin_id is None else str(node.basin_id)
        if node.sink_flag or (basin_id is not None and basin_id not in allowed_basin_ids):
            rejected.append(node_id)
    return tuple(sorted(rejected))


def _candidate_sort_key(candidate: LandscapeInferencePheromoneCandidate) -> tuple[float, int, str]:
    flux_score = 0.0 if candidate.mean_abs_flux is None else candidate.mean_abs_flux
    return (
        -float(candidate.flux_stability_score),
        -float(candidate.flux_observed_steps),
        -flux_score,
        len(candidate.path_edge_ids),
        candidate.candidate_id,
    )


def _basin_primitive_id(basin_id: str) -> str:
    return f"observed_basin_{_safe_id(basin_id)}"


def _deduplication_group_id(from_basin_id: str, to_basin_id: str) -> str:
    left, right = sorted((_safe_id(from_basin_id), _safe_id(to_basin_id)))
    return f"{left}__{right}"


def _pair_key(source: int, target: int) -> tuple[int, int]:
    a, b = int(source), int(target)
    return (a, b) if a <= b else (b, a)


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


def _sort_key(value: str) -> tuple[int, int | str]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)


__all__ = [
    "PHEROMONE_CLASSIFIER_ID",
    "PHEROMONE_CLASSIFIER_VERSION",
    "LandscapeInferencePheromoneCandidate",
    "classify_landscape_pheromone_candidates",
    "infer_landscape_pheromone_seed",
    "select_emitted_landscape_pheromone_candidates",
]
