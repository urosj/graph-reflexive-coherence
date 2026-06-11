"""Collapse/revival diagnostic probe for pheromone path-memory evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference_loader import LandscapeInferenceArtifactLoadResult
from .inference_pheromone import (
    classify_landscape_pheromone_candidates,
    select_emitted_landscape_pheromone_candidates,
)
from .inference_substrate import (
    LandscapeInferenceCheckpointGraph,
    LandscapeInferenceEvidenceSubstrate,
    build_landscape_inference_evidence_substrate,
)


REVIVAL_PROBE_ID = "landscape_inference_pheromone_revival_probe"
REVIVAL_PROBE_VERSION = "landscape_inference_optional_revival_v1"

_EMPHASIS_EVENT_KINDS = frozenset(("choice_detected", "collapse"))


@dataclass(frozen=True)
class LandscapeInferenceRevivalCandidate:
    """Node-level revival diagnostic around collapse/choice emphasis."""

    node_id: int
    event_refs: tuple[str, ...]
    first_event_step: int
    checkpoint_ids: tuple[str, ...]
    step_indices: tuple[int, ...]
    activity_series: tuple[float | None, ...]
    low_activity_step: int | None
    low_activity_value: float | None
    max_later_activity_step: int | None
    max_later_activity_value: float | None
    revival_delta: float | None
    revived_after_emphasis: bool
    status: str
    pheromone_candidate_count: int
    strongest_pheromone_score: float | None
    strongest_pheromone_candidate_id: str | None
    policy_suggestions: tuple[str, ...]
    evidence_fields: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "node_id": self.node_id,
                "event_refs": list(self.event_refs),
                "first_event_step": self.first_event_step,
                "checkpoint_ids": list(self.checkpoint_ids),
                "step_indices": list(self.step_indices),
                "activity_series": list(self.activity_series),
                "low_activity_step": self.low_activity_step,
                "low_activity_value": self.low_activity_value,
                "max_later_activity_step": self.max_later_activity_step,
                "max_later_activity_value": self.max_later_activity_value,
                "revival_delta": self.revival_delta,
                "revived_after_emphasis": self.revived_after_emphasis,
                "status": self.status,
                "pheromone_candidate_count": self.pheromone_candidate_count,
                "strongest_pheromone_score": self.strongest_pheromone_score,
                "strongest_pheromone_candidate_id": self.strongest_pheromone_candidate_id,
                "policy_suggestions": list(self.policy_suggestions),
                "evidence_fields": list(self.evidence_fields),
            }
        )


@dataclass(frozen=True)
class LandscapeInferenceRevivalProbeReport:
    """Replayable diagnostic report for revival/path-memory probes."""

    artifact_root: str
    runtime_family: str
    inference_window: Mapping[str, Any]
    candidate_count: int
    revived_candidate_count: int
    pheromone_associated_candidate_count: int
    candidates: tuple[LandscapeInferenceRevivalCandidate, ...]
    probe_id: str = REVIVAL_PROBE_ID
    probe_version: str = REVIVAL_PROBE_VERSION

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "probe_id": self.probe_id,
                "probe_version": self.probe_version,
                "artifact_root": self.artifact_root,
                "runtime_family": self.runtime_family,
                "inference_window": dict(self.inference_window),
                "candidate_count": self.candidate_count,
                "revived_candidate_count": self.revived_candidate_count,
                "pheromone_associated_candidate_count": self.pheromone_associated_candidate_count,
                "candidates": [candidate.to_mapping() for candidate in self.candidates],
            }
        )


def run_landscape_inference_revival_probe(
    load_result: LandscapeInferenceArtifactLoadResult,
    *,
    substrate: LandscapeInferenceEvidenceSubstrate | None = None,
    revival_delta_threshold: float = 1e-9,
) -> LandscapeInferenceRevivalProbeReport:
    """Detect event-emphasized nodes that regain activity later in the window."""

    resolved_substrate = substrate or build_landscape_inference_evidence_substrate(
        load_result,
        allow_short_persistence_window=True,
    )
    events_by_node = _emphasis_events_by_node(load_result)
    pheromones = select_emitted_landscape_pheromone_candidates(
        classify_landscape_pheromone_candidates(load_result, substrate=resolved_substrate)
    )
    candidates = tuple(
        _candidate_for_node(
            node_id,
            event_refs,
            load_result,
            resolved_substrate,
            pheromones,
            revival_delta_threshold=revival_delta_threshold,
        )
        for node_id, event_refs in sorted(events_by_node.items())
    )
    return LandscapeInferenceRevivalProbeReport(
        artifact_root=str(load_result.artifact_root),
        runtime_family=load_result.source_runtime_family,
        inference_window=load_result.inference_window.to_mapping(),
        candidate_count=len(candidates),
        revived_candidate_count=sum(1 for candidate in candidates if candidate.revived_after_emphasis),
        pheromone_associated_candidate_count=sum(
            1 for candidate in candidates if candidate.pheromone_candidate_count > 0
        ),
        candidates=candidates,
    )


def write_landscape_inference_revival_probe_report(
    report: LandscapeInferenceRevivalProbeReport,
    output_root: str | Path,
    *,
    json_name: str = "revival_probe_report.json",
    markdown_name: str = "README.md",
) -> tuple[Path, Path]:
    """Write JSON and Markdown revival probe reports."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / json_name
    markdown_path = root / markdown_name
    json_path.write_text(
        json.dumps(report.to_mapping(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(_report_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def _candidate_for_node(
    node_id: int,
    event_refs: Sequence[str],
    load_result: LandscapeInferenceArtifactLoadResult,
    substrate: LandscapeInferenceEvidenceSubstrate,
    pheromones: Sequence[Any],
    *,
    revival_delta_threshold: float,
) -> LandscapeInferenceRevivalCandidate:
    first_event_step = min(_event_step(ref) for ref in event_refs)
    step_indices = tuple(graph.step_index for graph in substrate.checkpoint_graphs)
    activity_series = tuple(_node_activity(graph, node_id) for graph in substrate.checkpoint_graphs)
    low_index, low_value, high_index, high_value, delta = _revival_window(
        step_indices,
        activity_series,
        first_event_step=first_event_step,
    )
    revived = delta is not None and delta > revival_delta_threshold
    related_pheromones = tuple(
        candidate for candidate in pheromones if int(node_id) in set(candidate.path_node_ids)
    )
    strongest = None
    if related_pheromones:
        strongest = max(
            related_pheromones,
            key=lambda candidate: (
                candidate.flux_stability_score,
                candidate.flux_observed_steps,
                candidate.candidate_id,
            ),
        )
    suggestions: list[str] = []
    if revived and related_pheromones:
        suggestions.append("test_path_memory_feedback_to_delay_or_suppress_revival")
    elif revived:
        suggestions.append("monitor_revival_without_path_memory_support")
    elif related_pheromones:
        suggestions.append("monitor_path_memory_without_revival")
    return LandscapeInferenceRevivalCandidate(
        node_id=int(node_id),
        event_refs=tuple(event_refs),
        first_event_step=first_event_step,
        checkpoint_ids=tuple(graph.checkpoint_id for graph in substrate.checkpoint_graphs),
        step_indices=step_indices,
        activity_series=activity_series,
        low_activity_step=None if low_index is None else step_indices[low_index],
        low_activity_value=low_value,
        max_later_activity_step=None if high_index is None else step_indices[high_index],
        max_later_activity_value=high_value,
        revival_delta=delta,
        revived_after_emphasis=revived,
        status=_candidate_status(revived=revived, related_pheromones=related_pheromones),
        pheromone_candidate_count=len(related_pheromones),
        strongest_pheromone_score=None if strongest is None else strongest.flux_stability_score,
        strongest_pheromone_candidate_id=None if strongest is None else strongest.candidate_id,
        policy_suggestions=tuple(suggestions),
        evidence_fields=_evidence_fields(related_pheromones),
    )


def _node_activity(graph: LandscapeInferenceCheckpointGraph, node_id: int) -> float | None:
    node = graph.nodes.get(int(node_id))
    if node is None:
        return None
    coherence = 0.0 if node.coherence is None else max(0.0, float(node.coherence))
    incident_flux = 0.0
    for edge in graph.edges.values():
        if edge.source_node_id != node_id and edge.target_node_id != node_id:
            continue
        if edge.signed_flux is not None:
            incident_flux += abs(float(edge.signed_flux))
    return float(coherence + incident_flux)


def _revival_window(
    step_indices: Sequence[int],
    activity_series: Sequence[float | None],
    *,
    first_event_step: int,
) -> tuple[int | None, float | None, int | None, float | None, float | None]:
    indexed = tuple(
        (index, value)
        for index, (step, value) in enumerate(zip(step_indices, activity_series))
        if step >= first_event_step and value is not None
    )
    if len(indexed) < 2:
        return (None, None, None, None, None)
    low_index, low_value = min(indexed, key=lambda item: (float(item[1]), item[0]))
    later = tuple((index, value) for index, value in indexed if index > low_index)
    if not later:
        return (low_index, float(low_value), None, None, None)
    high_index, high_value = max(later, key=lambda item: (float(item[1]), -item[0]))
    return (
        low_index,
        float(low_value),
        high_index,
        float(high_value),
        float(high_value) - float(low_value),
    )


def _emphasis_events_by_node(
    load_result: LandscapeInferenceArtifactLoadResult,
) -> dict[int, tuple[str, ...]]:
    grouped: dict[int, list[str]] = {}
    for row in load_result.telemetry_pack.event_rows:
        if str(row.event_kind) not in _EMPHASIS_EVENT_KINDS:
            continue
        node_id = _primary_node_id(row)
        if node_id is None:
            continue
        grouped.setdefault(node_id, []).append(
            f"step_{int(row.step_index)}:event_{int(row.event_index)}:{row.event_kind}"
        )
    return {node_id: tuple(refs) for node_id, refs in grouped.items()}


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


def _candidate_status(*, revived: bool, related_pheromones: Sequence[Any]) -> str:
    if revived and related_pheromones:
        return "revived_with_path_memory"
    if revived:
        return "revived_without_path_memory"
    if related_pheromones:
        return "path_memory_without_revival"
    return "monitored_no_revival"


def _evidence_fields(related_pheromones: Sequence[Any]) -> tuple[str, ...]:
    fields = [
        "events.event_kind",
        "events.primary_node_id",
        "graph_checkpoints.node_records.coherence",
        "graph_checkpoints.edge_records.signed_flux",
    ]
    if related_pheromones:
        fields.append("graph_checkpoints.path_flux_stability.stability_score")
    return tuple(fields)


def _event_step(ref: str) -> int:
    first = ref.split(":", 1)[0]
    return int(first.removeprefix("step_"))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _report_markdown(report: LandscapeInferenceRevivalProbeReport) -> str:
    lines = [
        "# Pheromone Revival Probe",
        "",
        f"- artifact: `{report.artifact_root}`",
        f"- runtime: `{report.runtime_family}`",
        f"- window: `{dict(report.inference_window)}`",
        f"- candidates: {report.candidate_count}",
        f"- revived candidates: {report.revived_candidate_count}",
        f"- path-memory-associated candidates: {report.pheromone_associated_candidate_count}",
        "",
        "## Candidates",
        "",
    ]
    for candidate in report.candidates:
        lines.extend(
            [
                f"- node `{candidate.node_id}`: `{candidate.status}`",
                f"  - events: `{candidate.event_refs}`",
                f"  - low: step `{candidate.low_activity_step}` value `{candidate.low_activity_value}`",
                f"  - later max: step `{candidate.max_later_activity_step}` value `{candidate.max_later_activity_value}`",
                f"  - revival delta: `{candidate.revival_delta}`",
                f"  - pheromone candidates: `{candidate.pheromone_candidate_count}`",
                f"  - policy suggestions: `{candidate.policy_suggestions}`",
            ]
        )
    return "\n".join(lines) + "\n"


__all__ = [
    "REVIVAL_PROBE_ID",
    "REVIVAL_PROBE_VERSION",
    "LandscapeInferenceRevivalCandidate",
    "LandscapeInferenceRevivalProbeReport",
    "run_landscape_inference_revival_probe",
    "write_landscape_inference_revival_probe_report",
]
