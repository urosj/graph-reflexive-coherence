"""Authored-vs-observed landscape primitive comparison."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .io import landscape_seed_from_data, load_landscape_seed
from .seed import LandscapePrimitive, LandscapeSeed


COMPARISON_CLASSIFIER_ID = "landscape_inference_primitive_comparison"
COMPARISON_CLASSIFIER_VERSION = "landscape_inference_iter8_v1"


@dataclass(frozen=True)
class LandscapeInferencePrimitiveMatchCandidate:
    """Candidate match between one authored and one observed primitive."""

    authored_id: str
    observed_id: str
    score: float
    match_mode: str
    relationship: str
    provenance_available: bool
    evidence: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "authored_id": self.authored_id,
                "observed_id": self.observed_id,
                "score": self.score,
                "match_mode": self.match_mode,
                "relationship": self.relationship,
                "provenance_available": self.provenance_available,
                "evidence": list(self.evidence),
            }
        )


@dataclass(frozen=True)
class LandscapeInferencePrimitiveComparisonRecord:
    """Final comparison record emitted by Iteration 8."""

    relationship: str
    authored_ids: tuple[str, ...]
    observed_ids: tuple[str, ...]
    match_mode: str
    confidence: float
    provenance_available: bool
    evidence: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "relationship": self.relationship,
                "authored_ids": list(self.authored_ids),
                "observed_ids": list(self.observed_ids),
                "match_mode": self.match_mode,
                "confidence": self.confidence,
                "provenance_available": self.provenance_available,
                "evidence": list(self.evidence),
                "notes": list(self.notes),
            }
        )


@dataclass(frozen=True)
class LandscapeInferenceComparisonReport:
    """Deterministic authored-vs-observed comparison report."""

    authored_name: str
    observed_name: str
    candidate_count: int
    records: tuple[LandscapeInferencePrimitiveComparisonRecord, ...]
    classifier_id: str = COMPARISON_CLASSIFIER_ID
    classifier_version: str = COMPARISON_CLASSIFIER_VERSION

    def to_mapping(self) -> dict[str, Any]:
        relationship_counts: dict[str, int] = defaultdict(int)
        for record in self.records:
            relationship_counts[record.relationship] += 1
        return canonicalize_json_value(
            {
                "classifier_id": self.classifier_id,
                "classifier_version": self.classifier_version,
                "authored_name": self.authored_name,
                "observed_name": self.observed_name,
                "candidate_count": self.candidate_count,
                "relationship_counts": dict(sorted(relationship_counts.items())),
                "records": [record.to_mapping() for record in self.records],
            }
        )


def compare_landscape_seeds(
    authored_seed: LandscapeSeed | Mapping[str, Any],
    observed_seed: LandscapeSeed | Mapping[str, Any],
    *,
    role_fallback_min_score: float = 0.4,
) -> LandscapeInferenceComparisonReport:
    """Compare authored/source primitives with observed inferred primitives."""

    authored = _coerce_seed(authored_seed)
    observed = _coerce_seed(observed_seed)
    candidates = _match_candidates(authored.primitives, observed.primitives)
    strong_pairs = tuple(candidate for candidate in candidates if candidate.score >= 0.7)
    if not strong_pairs:
        strong_pairs = _best_role_fallbacks(candidates, min_score=role_fallback_min_score)

    authored_to_observed: dict[str, list[LandscapeInferencePrimitiveMatchCandidate]] = defaultdict(list)
    observed_to_authored: dict[str, list[LandscapeInferencePrimitiveMatchCandidate]] = defaultdict(list)
    for candidate in strong_pairs:
        authored_to_observed[candidate.authored_id].append(candidate)
        observed_to_authored[candidate.observed_id].append(candidate)

    records: list[LandscapeInferencePrimitiveComparisonRecord] = []
    consumed_authored: set[str] = set()
    consumed_observed: set[str] = set()

    for authored_id, matches in sorted(authored_to_observed.items()):
        unique_observed = tuple(sorted({match.observed_id for match in matches}))
        if len(unique_observed) <= 1:
            continue
        records.append(
            _group_record(
                relationship="split",
                authored_ids=(authored_id,),
                observed_ids=unique_observed,
                matches=matches,
                notes=("one authored primitive maps to multiple observed primitives",),
            )
        )
        consumed_authored.add(authored_id)
        consumed_observed.update(unique_observed)

    for observed_id, matches in sorted(observed_to_authored.items()):
        unique_authored = tuple(sorted({match.authored_id for match in matches}))
        if len(unique_authored) <= 1:
            continue
        records.append(
            _group_record(
                relationship="collapsed",
                authored_ids=unique_authored,
                observed_ids=(observed_id,),
                matches=matches,
                notes=("multiple authored primitives map to one observed primitive",),
            )
        )
        consumed_authored.update(unique_authored)
        consumed_observed.add(observed_id)

    for candidate in strong_pairs:
        if candidate.authored_id in consumed_authored or candidate.observed_id in consumed_observed:
            continue
        records.append(
            LandscapeInferencePrimitiveComparisonRecord(
                relationship=candidate.relationship,
                authored_ids=(candidate.authored_id,),
                observed_ids=(candidate.observed_id,),
                match_mode=candidate.match_mode,
                confidence=candidate.score,
                provenance_available=candidate.provenance_available,
                evidence=candidate.evidence,
            )
        )
        consumed_authored.add(candidate.authored_id)
        consumed_observed.add(candidate.observed_id)

    authored_ids = {primitive.id for primitive in authored.primitives}
    observed_ids = {primitive.id for primitive in observed.primitives}
    for observed_id in sorted(observed_ids - consumed_observed):
        records.append(
            LandscapeInferencePrimitiveComparisonRecord(
                relationship="emerged",
                authored_ids=(),
                observed_ids=(observed_id,),
                match_mode="unmatched_observed",
                confidence=0.5,
                provenance_available=False,
                evidence=("observed_seed.primitives.id",),
            )
        )
    for authored_id in sorted(authored_ids - consumed_authored):
        records.append(
            LandscapeInferencePrimitiveComparisonRecord(
                relationship="dissolved",
                authored_ids=(authored_id,),
                observed_ids=(),
                match_mode="unmatched_authored",
                confidence=0.5,
                provenance_available=False,
                evidence=("authored_seed.primitives.id",),
            )
        )
    return LandscapeInferenceComparisonReport(
        authored_name=authored.meta.name,
        observed_name=observed.meta.name,
        candidate_count=len(candidates),
        records=tuple(sorted(records, key=_record_sort_key)),
    )


def compare_landscape_seed_files(
    authored_path: str | Path,
    observed_path: str | Path,
) -> LandscapeInferenceComparisonReport:
    """Load and compare two landscape seed documents."""

    return compare_landscape_seeds(
        load_landscape_seed(authored_path),
        load_landscape_seed(observed_path),
    )


def write_landscape_inference_comparison_report(
    report: LandscapeInferenceComparisonReport,
    output_root: str | Path,
    *,
    json_name: str = "comparison_report.json",
    markdown_name: str = "README.md",
) -> tuple[Path, Path]:
    """Write JSON and Markdown comparison reports."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / json_name
    markdown_path = root / markdown_name
    json_path.write_text(
        _json_dumps(report.to_mapping()),
        encoding="utf-8",
    )
    markdown_path.write_text(_comparison_markdown(report), encoding="utf-8")
    return (json_path, markdown_path)


def _match_candidates(
    authored: Sequence[LandscapePrimitive],
    observed: Sequence[LandscapePrimitive],
) -> tuple[LandscapeInferencePrimitiveMatchCandidate, ...]:
    candidates: list[LandscapeInferencePrimitiveMatchCandidate] = []
    for authored_primitive in authored:
        for observed_primitive in observed:
            candidate = _match_candidate(authored_primitive, observed_primitive)
            if candidate is not None:
                candidates.append(candidate)
    return tuple(sorted(candidates, key=lambda item: (-item.score, item.authored_id, item.observed_id)))


def _match_candidate(
    authored: LandscapePrimitive,
    observed: LandscapePrimitive,
) -> LandscapeInferencePrimitiveMatchCandidate | None:
    provenance_available = bool(_primitive_provenance_ids(authored) or _primitive_provenance_ids(observed))
    observed_match = _observed_matched_authored_id(observed)
    if observed_match == authored.id or authored.id in _primitive_provenance_ids(observed):
        return LandscapeInferencePrimitiveMatchCandidate(
            authored_id=authored.id,
            observed_id=observed.id,
            score=0.98,
            match_mode="provenance",
            relationship="preserved",
            provenance_available=True,
            evidence=("primitive.extensions.landscape_inference.matched_authored_primitive_id",),
        )
    topology_overlap = _topology_overlap(authored, observed)
    if topology_overlap:
        relationship = "preserved" if authored.type == observed.type else "transformed"
        return LandscapeInferencePrimitiveMatchCandidate(
            authored_id=authored.id,
            observed_id=observed.id,
            score=0.74 if relationship == "preserved" else 0.68,
            match_mode="topology",
            relationship=relationship,
            provenance_available=provenance_available,
            evidence=topology_overlap,
        )
    if _role_geometry_compatible(authored, observed):
        relationship = "preserved" if authored.type == observed.type else "transformed"
        return LandscapeInferencePrimitiveMatchCandidate(
            authored_id=authored.id,
            observed_id=observed.id,
            score=0.46 if relationship == "preserved" else 0.42,
            match_mode="role_geometry",
            relationship=relationship,
            provenance_available=provenance_available,
            evidence=("primitive.type", "primitive.role"),
        )
    return None


def _best_role_fallbacks(
    candidates: Sequence[LandscapeInferencePrimitiveMatchCandidate],
    *,
    min_score: float,
) -> tuple[LandscapeInferencePrimitiveMatchCandidate, ...]:
    best_by_observed: dict[str, LandscapeInferencePrimitiveMatchCandidate] = {}
    for candidate in candidates:
        if candidate.score < min_score:
            continue
        current = best_by_observed.get(candidate.observed_id)
        if current is None or _candidate_sort_key(candidate) < _candidate_sort_key(current):
            best_by_observed[candidate.observed_id] = candidate
    return tuple(sorted(best_by_observed.values(), key=lambda item: (item.authored_id, item.observed_id)))


def _group_record(
    *,
    relationship: str,
    authored_ids: tuple[str, ...],
    observed_ids: tuple[str, ...],
    matches: Sequence[LandscapeInferencePrimitiveMatchCandidate],
    notes: tuple[str, ...],
) -> LandscapeInferencePrimitiveComparisonRecord:
    confidence = max(match.score for match in matches) if matches else 0.0
    provenance_available = any(match.provenance_available for match in matches)
    modes = tuple(sorted({match.match_mode for match in matches}))
    evidence = tuple(sorted({field for match in matches for field in match.evidence}))
    return LandscapeInferencePrimitiveComparisonRecord(
        relationship=relationship,
        authored_ids=tuple(sorted(authored_ids)),
        observed_ids=tuple(sorted(observed_ids)),
        match_mode="+".join(modes),
        confidence=confidence,
        provenance_available=provenance_available,
        evidence=evidence,
        notes=notes,
    )


def _topology_overlap(authored: LandscapePrimitive, observed: LandscapePrimitive) -> tuple[str, ...]:
    evidence: list[str] = []
    authored_endpoints = _endpoint_ids(authored)
    observed_endpoints = _endpoint_ids(observed)
    if authored_endpoints and observed_endpoints and authored_endpoints == observed_endpoints:
        evidence.append("primitive.endpoint_ids")
    authored_path = _path_node_ids(authored)
    observed_path = _path_node_ids(observed)
    if authored_path and observed_path and set(authored_path) & set(observed_path):
        evidence.append("primitive.path_node_ids")
    authored_containment = _containment_ids(authored)
    observed_containment = _containment_ids(observed)
    if authored_containment and observed_containment and authored_containment & observed_containment:
        evidence.append("primitive.containment_ids")
    return tuple(evidence)


def _role_geometry_compatible(authored: LandscapePrimitive, observed: LandscapePrimitive) -> bool:
    if authored.type != observed.type:
        return False
    return bool(_role_tokens(authored) & _role_tokens(observed))


def _endpoint_ids(primitive: LandscapePrimitive) -> tuple[str, ...]:
    values: list[str] = []
    for key in ("from_id", "to_id"):
        value = getattr(primitive, key, None)
        if value is not None:
            values.append(str(value))
    return tuple(sorted(values))


def _path_node_ids(primitive: LandscapePrimitive) -> tuple[int, ...]:
    inference = _mapping(primitive.extensions.get("landscape_inference"))
    evidence = _mapping(inference.get("evidence"))
    values = evidence.get("path_node_ids", ())
    if isinstance(values, Sequence) and not isinstance(values, str | bytes):
        result = []
        for value in values:
            parsed = _optional_int(value)
            if parsed is not None:
                result.append(parsed)
        return tuple(result)
    return ()


def _containment_ids(primitive: LandscapePrimitive) -> set[str]:
    values = {
        str(value)
        for value in (
            getattr(primitive, "parent_id", None),
            getattr(primitive, "owner_id", None),
            getattr(primitive, "host_id", None),
        )
        if value is not None
    }
    for value in getattr(primitive, "boundary_ids", ()):
        values.add(str(value))
    for value in getattr(primitive, "adjacent_ids", ()):
        values.add(str(value))
    for value in getattr(primitive, "branch_target_ids", ()):
        values.add(str(value))
    return values


def _role_tokens(primitive: LandscapePrimitive) -> set[str]:
    tokens = {str(primitive.type)}
    for attr in ("role", "junction_role", "channel_role", "ridge_kind", "stability_class"):
        value = getattr(primitive, attr, None)
        if value is not None:
            tokens.add(str(value))
    return tokens


def _primitive_provenance_ids(primitive: LandscapePrimitive) -> set[str]:
    ids: set[str] = set()
    _collect_provenance_ids(primitive.extensions, ids)
    return ids


def _collect_provenance_ids(value: Any, ids: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            if isinstance(key, str) and (
                key.endswith("source_id")
                or key.endswith("source_construct_id")
                or key.endswith("motif_id")
                or key == "matched_authored_primitive_id"
            ):
                if isinstance(inner, str) and inner:
                    ids.add(inner)
            _collect_provenance_ids(inner, ids)
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for item in value:
            _collect_provenance_ids(item, ids)


def _observed_matched_authored_id(primitive: LandscapePrimitive) -> str | None:
    inference = _mapping(primitive.extensions.get("landscape_inference"))
    value = inference.get("matched_authored_primitive_id")
    return str(value) if value else None


def _coerce_seed(value: LandscapeSeed | Mapping[str, Any]) -> LandscapeSeed:
    if isinstance(value, LandscapeSeed):
        return value
    return landscape_seed_from_data(dict(value))


def _record_sort_key(record: LandscapeInferencePrimitiveComparisonRecord) -> tuple[str, str, str]:
    return (
        record.relationship,
        ",".join(record.authored_ids),
        ",".join(record.observed_ids),
    )


def _candidate_sort_key(candidate: LandscapeInferencePrimitiveMatchCandidate) -> tuple[float, str, str]:
    return (-candidate.score, candidate.authored_id, candidate.observed_id)


def _comparison_markdown(report: LandscapeInferenceComparisonReport) -> str:
    mapping = report.to_mapping()
    lines = [
        "# Landscape Inference Authored-vs-Observed Comparison",
        "",
        f"- Classifier: `{report.classifier_version}`",
        f"- Authored: `{report.authored_name}`",
        f"- Observed: `{report.observed_name}`",
        f"- Candidate matches: `{report.candidate_count}`",
        f"- Relationship counts: `{mapping['relationship_counts']}`",
        "",
        "| Relationship | Authored | Observed | Mode | Confidence |",
        "|---|---|---|---|---:|",
    ]
    for record in report.records:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{record.relationship}`",
                    ", ".join(f"`{item}`" for item in record.authored_ids) or "-",
                    ", ".join(f"`{item}`" for item in record.observed_ids) or "-",
                    f"`{record.match_mode}`",
                    f"{record.confidence:.2f}",
                )
            )
            + " |"
        )
    lines.append("")
    lines.append("Split and collapse records are emitted explicitly when one-to-many or many-to-one matches are observed.")
    return "\n".join(lines) + "\n"


def _json_dumps(value: Any) -> str:
    import json

    return json.dumps(canonicalize_json_value(value), indent=2, sort_keys=True) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "COMPARISON_CLASSIFIER_ID",
    "COMPARISON_CLASSIFIER_VERSION",
    "LandscapeInferenceComparisonReport",
    "LandscapeInferencePrimitiveComparisonRecord",
    "LandscapeInferencePrimitiveMatchCandidate",
    "compare_landscape_seed_files",
    "compare_landscape_seeds",
    "write_landscape_inference_comparison_report",
]
