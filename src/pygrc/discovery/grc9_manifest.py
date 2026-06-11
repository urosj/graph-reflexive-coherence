"""Manifest contract for GRC9 phenomenology discovery artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import re
from typing import Any


GRC9_DISCOVERY_FAMILY = "grc9"
GRC9_DISCOVERY_TRACK = "phenomenology_discovery"
GRC9_DISCOVERY_PROGRAM = "grc9_phenomenology_discovery"
GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION = (
    "grc9_phenomenology_discovery_v1"
)

DISCOVERY_OUTPUT_ROOT = "outputs/discovery/grc9"
DISCOVERY_SESSION_ROOT = "outputs/grc9/phenomenology_discovery/sessions"
DISCOVERY_PROFILE_NAMING = "grc9_discovery_<phenomenon>_v<integer>"
DISCOVERY_LANE_NAMING = "<seed_family>_<control_role>"

_TOKEN_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_PROFILE_RE = re.compile(r"^grc9_discovery_[a-z0-9]+(?:_[a-z0-9]+)*_v[1-9][0-9]*$")
_SESSION_RE = re.compile(r"^S[0-9]{4}$")

_CONTROL_ROLES = frozenset(
    {
        "positive_control",
        "negative_control",
        "neutral_control",
        "baseline_control",
        "diagnostic_control",
        "complex_control",
        "perturbation_control",
        "no_event_control",
    }
)
_RUNTIME_STATUSES = frozenset({"testable", "deferred", "reserved_future", "out_of_scope"})
_CONFIDENCE_LABELS = frozenset(
    {"rejected", "needs-rerun", "weak_candidate", "candidate", "strong_candidate", "accepted_after_review"}
)
_REVIEW_STATUSES = frozenset(
    {
        "unreviewed",
        "candidate",
        "weak_candidate",
        "strong_candidate",
        "accepted",
        "rejected",
        "duplicate",
        "needs-rerun",
    }
)


def _require_string(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _optional_string(value: Any, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, field_name=field_name)


def _require_bool(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean")
    return value


def _require_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    return value


def _require_mapping(value: Any, *, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def _require_sequence(value: Any, *, field_name: str) -> Sequence[Any]:
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence")
    return value


def _string_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    return tuple(
        _require_string(item, field_name=f"{field_name}[{index}]")
        for index, item in enumerate(_require_sequence(value, field_name=field_name))
    )


def _mapping_copy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _validate_token(value: str, *, field_name: str) -> None:
    _require_string(value, field_name=field_name)
    if not _TOKEN_RE.fullmatch(value):
        raise ValueError(f"{field_name} must use lowercase snake-case tokens")


def _normalize_delta(delta: str) -> str:
    value = _require_string(delta, field_name="delta")
    value = value.replace("+", "plus").replace("-", "minus").replace("%", "pct")
    value = value.replace(".", "p")
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_").lower()
    _validate_token(value, field_name="normalized delta")
    return value


def profile_name(phenomenon: str, version: int) -> str:
    """Return the standard discovery profile name."""

    _validate_token(phenomenon, field_name="phenomenon")
    if isinstance(version, bool) or not isinstance(version, int) or version <= 0:
        raise ValueError("version must be a positive integer")
    return f"grc9_discovery_{phenomenon}_v{version}"


def generated_lane_name(seed_family: str, control_role: str) -> str:
    """Return the standard generated discovery lane name."""

    _validate_token(seed_family, field_name="seed_family")
    _validate_token(control_role, field_name="control_role")
    if control_role not in _CONTROL_ROLES:
        raise ValueError(f"control_role must be one of {tuple(sorted(_CONTROL_ROLES))}")
    return f"{seed_family}_{control_role}"


def perturbation_lane_name(
    seed_family: str,
    control_role: str,
    parameter: str,
    delta: str,
) -> str:
    """Return the standard generated perturbation lane name."""

    _validate_token(parameter, field_name="parameter")
    return f"{generated_lane_name(seed_family, control_role)}_{parameter}_{_normalize_delta(delta)}"


def is_discovery_profile_name(value: str) -> bool:
    return bool(_PROFILE_RE.fullmatch(value))


def is_generated_lane_name(value: str) -> bool:
    if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
        return False
    if (
        value.endswith("_emitter")
        or value.endswith("_combo")
        or value.endswith("_control")
        or value.endswith("_pass")
        or value.endswith("_fail")
        or value.endswith("_high")
        or value.endswith("_low")
    ):
        return True
    for role in _CONTROL_ROLES:
        suffix = f"_{role}"
        marker = f"{suffix}_"
        if value.endswith(suffix):
            return bool(value[: -len(suffix)])
        if marker in value:
            prefix, suffix_payload = value.split(marker, 1)
            return bool(prefix and _TOKEN_RE.fullmatch(prefix) and suffix_payload)
    return False


def is_session_id(value: str) -> bool:
    return bool(_SESSION_RE.fullmatch(value))


@dataclass(frozen=True)
class GRC9SourceArtifact:
    artifact_role: str
    path: str
    used_for_discovery: bool

    def __post_init__(self) -> None:
        _validate_token(self.artifact_role, field_name="artifact_role")
        _require_string(self.path, field_name="path")
        _require_bool(self.used_for_discovery, field_name="used_for_discovery")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "artifact_role": self.artifact_role,
            "path": self.path,
            "used_for_discovery": self.used_for_discovery,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9SourceArtifact:
        mapping = _require_mapping(value, field_name="source_artifact")
        return cls(
            artifact_role=_require_string(mapping.get("artifact_role"), field_name="artifact_role"),
            path=_require_string(mapping.get("path"), field_name="path"),
            used_for_discovery=_require_bool(
                mapping.get("used_for_discovery"),
                field_name="used_for_discovery",
            ),
        )


@dataclass(frozen=True)
class GRC9ManifestRunScope:
    family: str = GRC9_DISCOVERY_FAMILY
    profile_naming: str = DISCOVERY_PROFILE_NAMING
    lane_naming: str = DISCOVERY_LANE_NAMING
    profiles: tuple[str, ...] = ()
    lanes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.family != GRC9_DISCOVERY_FAMILY:
            raise ValueError("run_scope.family must be 'grc9'")
        for profile in self.profiles:
            if not is_discovery_profile_name(profile):
                raise ValueError(f"invalid discovery profile name {profile!r}")
        for lane in self.lanes:
            if not is_generated_lane_name(lane):
                raise ValueError(f"invalid generated lane name {lane!r}")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "family": self.family,
            "profile_naming": self.profile_naming,
            "lane_naming": self.lane_naming,
            "profiles": list(self.profiles),
            "lanes": list(self.lanes),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9ManifestRunScope:
        mapping = _require_mapping(value, field_name="run_scope")
        return cls(
            family=_require_string(mapping.get("family", GRC9_DISCOVERY_FAMILY), field_name="family"),
            profile_naming=_require_string(
                mapping.get("profile_naming", DISCOVERY_PROFILE_NAMING),
                field_name="profile_naming",
            ),
            lane_naming=_require_string(
                mapping.get("lane_naming", DISCOVERY_LANE_NAMING),
                field_name="lane_naming",
            ),
            profiles=_string_tuple(mapping.get("profiles", []), field_name="profiles"),
            lanes=_string_tuple(mapping.get("lanes", []), field_name="lanes"),
        )


@dataclass(frozen=True)
class GRC9SourceReference:
    source: str
    section: str = ""
    equation: str = ""

    def __post_init__(self) -> None:
        _require_string(self.source, field_name="source")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "source": self.source,
            "section": self.section,
            "equation": self.equation,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9SourceReference:
        mapping = _require_mapping(value, field_name="source_reference")
        return cls(
            source=_require_string(mapping.get("source"), field_name="source"),
            section=str(mapping.get("section", "")),
            equation=str(mapping.get("equation", "")),
        )


@dataclass(frozen=True)
class GRC9PredictedSignature:
    field_path: str
    predicate: str
    expected_type: str | None = None
    required: bool = True

    def __post_init__(self) -> None:
        _require_string(self.field_path, field_name="field_path")
        _require_string(self.predicate, field_name="predicate")
        _require_bool(self.required, field_name="required")

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "field_path": self.field_path,
            "predicate": self.predicate,
            "required": self.required,
        }
        if self.expected_type is not None:
            payload["expected_type"] = self.expected_type
        return payload

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9PredictedSignature:
        mapping = _require_mapping(value, field_name="predicted_signature")
        return cls(
            field_path=_require_string(mapping.get("field_path"), field_name="field_path"),
            predicate=_require_string(mapping.get("predicate"), field_name="predicate"),
            expected_type=_optional_string(mapping.get("expected_type"), field_name="expected_type"),
            required=_require_bool(mapping.get("required", True), field_name="required"),
        )


@dataclass(frozen=True)
class GRC9StructureHypothesis:
    hypothesis_id: str
    target_phenomenon: str
    runtime_status: str
    paper_sources: tuple[GRC9SourceReference, ...]
    graph_preconditions: Mapping[str, Any]
    seed_family: str
    seed_parameters: Mapping[str, Any]
    generator: str
    predicted_signatures: tuple[GRC9PredictedSignature, ...]

    def __post_init__(self) -> None:
        _validate_token(self.hypothesis_id, field_name="hypothesis_id")
        _validate_token(self.target_phenomenon, field_name="target_phenomenon")
        if self.runtime_status not in _RUNTIME_STATUSES:
            raise ValueError(f"runtime_status must be one of {tuple(sorted(_RUNTIME_STATUSES))}")
        _require_mapping(self.graph_preconditions, field_name="graph_preconditions")
        _validate_token(self.seed_family, field_name="seed_family")
        _require_mapping(self.seed_parameters, field_name="seed_parameters")
        _require_string(self.generator, field_name="generator")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "target_phenomenon": self.target_phenomenon,
            "runtime_status": self.runtime_status,
            "paper_sources": [item.to_mapping() for item in self.paper_sources],
            "graph_preconditions": dict(self.graph_preconditions),
            "seed_family": self.seed_family,
            "seed_parameters": dict(self.seed_parameters),
            "generator": self.generator,
            "predicted_signatures": [
                item.to_mapping() for item in self.predicted_signatures
            ],
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9StructureHypothesis:
        mapping = _require_mapping(value, field_name="structure_hypothesis")
        return cls(
            hypothesis_id=_require_string(mapping.get("hypothesis_id"), field_name="hypothesis_id"),
            target_phenomenon=_require_string(
                mapping.get("target_phenomenon"),
                field_name="target_phenomenon",
            ),
            runtime_status=_require_string(mapping.get("runtime_status"), field_name="runtime_status"),
            paper_sources=tuple(
                GRC9SourceReference.from_mapping(_require_mapping(item, field_name="paper_sources[]"))
                for item in _require_sequence(mapping.get("paper_sources", []), field_name="paper_sources")
            ),
            graph_preconditions=_mapping_copy(
                _require_mapping(mapping.get("graph_preconditions", {}), field_name="graph_preconditions")
            ),
            seed_family=_require_string(mapping.get("seed_family"), field_name="seed_family"),
            seed_parameters=_mapping_copy(
                _require_mapping(mapping.get("seed_parameters", {}), field_name="seed_parameters")
            ),
            generator=_require_string(mapping.get("generator"), field_name="generator"),
            predicted_signatures=tuple(
                GRC9PredictedSignature.from_mapping(
                    _require_mapping(item, field_name="predicted_signatures[]")
                )
                for item in _require_sequence(
                    mapping.get("predicted_signatures", []),
                    field_name="predicted_signatures",
                )
            ),
        )


@dataclass(frozen=True)
class GRC9SelectorSpec:
    selector_id: str
    surface: str
    query: str
    expected_type: str

    def __post_init__(self) -> None:
        _validate_token(self.selector_id, field_name="selector_id")
        _require_string(self.surface, field_name="surface")
        _require_string(self.query, field_name="query")
        _require_string(self.expected_type, field_name="expected_type")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "selector_id": self.selector_id,
            "surface": self.surface,
            "query": self.query,
            "expected_type": self.expected_type,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9SelectorSpec:
        mapping = _require_mapping(value, field_name="selector")
        return cls(
            selector_id=_require_string(mapping.get("selector_id"), field_name="selector_id"),
            surface=_require_string(mapping.get("surface"), field_name="surface"),
            query=_require_string(mapping.get("query"), field_name="query"),
            expected_type=_require_string(mapping.get("expected_type"), field_name="expected_type"),
        )


@dataclass(frozen=True)
class GRC9EvidenceFields:
    predicted: tuple[str, ...] = ()
    observed: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "predicted": list(self.predicted),
            "observed": list(self.observed),
            "missing": list(self.missing),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> GRC9EvidenceFields:
        mapping = _require_mapping(value or {}, field_name="evidence_fields")
        return cls(
            predicted=_string_tuple(mapping.get("predicted", []), field_name="evidence_fields.predicted"),
            observed=_string_tuple(mapping.get("observed", []), field_name="evidence_fields.observed"),
            missing=_string_tuple(mapping.get("missing", []), field_name="evidence_fields.missing"),
        )


@dataclass(frozen=True)
class GRC9MotifRecord:
    motif_id: str
    hypothesis_id: str
    phenomenon: str
    profile: str
    lane: str
    run_id: str
    seed_name: str
    step_window: tuple[int, int]
    family: str = GRC9_DISCOVERY_FAMILY
    session_ids: tuple[str, ...] = ()
    event_ids: tuple[str, ...] = ()
    checkpoint_ids: tuple[str, ...] = ()
    predicted_evidence_fields: tuple[str, ...] = ()
    observed_evidence_fields: tuple[str, ...] = ()
    evidence_fields: GRC9EvidenceFields = GRC9EvidenceFields()
    visual_artifacts: tuple[str, ...] = ()
    confidence_score: int = 0
    confidence_label: str = "candidate"
    review_status: str = "unreviewed"
    rejection_reason: str | None = None
    rerun_requested: bool = False
    non_claims: tuple[str, ...] = ()
    notes: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        _require_string(self.motif_id, field_name="motif_id")
        _validate_token(self.hypothesis_id, field_name="hypothesis_id")
        _validate_token(self.phenomenon, field_name="phenomenon")
        if self.family != GRC9_DISCOVERY_FAMILY:
            raise ValueError("motif.family must be 'grc9'")
        if not is_discovery_profile_name(self.profile):
            raise ValueError(f"invalid discovery profile name {self.profile!r}")
        if not is_generated_lane_name(self.lane):
            raise ValueError(f"invalid generated lane name {self.lane!r}")
        for session_id in self.session_ids:
            if not is_session_id(session_id):
                raise ValueError(f"invalid session id {session_id!r}")
        if len(self.step_window) != 2:
            raise ValueError("step_window must contain exactly two integers")
        start, end = self.step_window
        _require_int(start, field_name="step_window[0]")
        _require_int(end, field_name="step_window[1]")
        if start < 0 or end < start:
            raise ValueError("step_window must be non-negative and ordered")
        if self.confidence_score < 0 or self.confidence_score > 5:
            raise ValueError("confidence_score must be in [0, 5]")
        if self.confidence_label not in _CONFIDENCE_LABELS:
            raise ValueError("confidence_label is not recognized")
        if self.review_status not in _REVIEW_STATUSES:
            raise ValueError("review_status is not recognized")
        _require_bool(self.rerun_requested, field_name="rerun_requested")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "hypothesis_id": self.hypothesis_id,
            "phenomenon": self.phenomenon,
            "family": self.family,
            "profile": self.profile,
            "lane": self.lane,
            "run_id": self.run_id,
            "seed_name": self.seed_name,
            "session_ids": list(self.session_ids),
            "step_window": list(self.step_window),
            "event_ids": list(self.event_ids),
            "checkpoint_ids": list(self.checkpoint_ids),
            "predicted_evidence_fields": list(self.predicted_evidence_fields),
            "observed_evidence_fields": list(self.observed_evidence_fields),
            "evidence_fields": self.evidence_fields.to_mapping(),
            "visual_artifacts": list(self.visual_artifacts),
            "confidence_score": self.confidence_score,
            "confidence_label": self.confidence_label,
            "review_status": self.review_status,
            "rejection_reason": self.rejection_reason,
            "rerun_requested": self.rerun_requested,
            "non_claims": list(self.non_claims),
            "notes": dict(self.notes or {}),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9MotifRecord:
        mapping = _require_mapping(value, field_name="motif")
        step_window_raw = _require_sequence(mapping.get("step_window", [0, 0]), field_name="step_window")
        return cls(
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            hypothesis_id=_require_string(mapping.get("hypothesis_id"), field_name="hypothesis_id"),
            phenomenon=_require_string(mapping.get("phenomenon"), field_name="phenomenon"),
            family=_require_string(mapping.get("family", GRC9_DISCOVERY_FAMILY), field_name="family"),
            profile=_require_string(mapping.get("profile"), field_name="profile"),
            lane=_require_string(mapping.get("lane"), field_name="lane"),
            run_id=str(mapping.get("run_id", "")),
            seed_name=_require_string(mapping.get("seed_name"), field_name="seed_name"),
            session_ids=_string_tuple(mapping.get("session_ids", []), field_name="session_ids"),
            step_window=(
                _require_int(step_window_raw[0], field_name="step_window[0]"),
                _require_int(step_window_raw[1], field_name="step_window[1]"),
            ),
            event_ids=_string_tuple(mapping.get("event_ids", []), field_name="event_ids"),
            checkpoint_ids=_string_tuple(mapping.get("checkpoint_ids", []), field_name="checkpoint_ids"),
            predicted_evidence_fields=_string_tuple(
                mapping.get("predicted_evidence_fields", []),
                field_name="predicted_evidence_fields",
            ),
            observed_evidence_fields=_string_tuple(
                mapping.get("observed_evidence_fields", []),
                field_name="observed_evidence_fields",
            ),
            evidence_fields=GRC9EvidenceFields.from_mapping(mapping.get("evidence_fields")),
            visual_artifacts=_string_tuple(mapping.get("visual_artifacts", []), field_name="visual_artifacts"),
            confidence_score=_require_int(mapping.get("confidence_score", 0), field_name="confidence_score"),
            confidence_label=_require_string(mapping.get("confidence_label", "candidate"), field_name="confidence_label"),
            review_status=_require_string(mapping.get("review_status", "unreviewed"), field_name="review_status"),
            rejection_reason=_optional_string(mapping.get("rejection_reason"), field_name="rejection_reason"),
            rerun_requested=_require_bool(mapping.get("rerun_requested", False), field_name="rerun_requested"),
            non_claims=_string_tuple(mapping.get("non_claims", []), field_name="non_claims"),
            notes=dict(_require_mapping(mapping.get("notes", {}), field_name="notes")),
        )


@dataclass(frozen=True)
class GRC9ReviewHistoryEntry:
    motif_id: str
    from_status: str
    to_status: str
    reviewer: str
    reason: str
    timestamp_utc: str

    def __post_init__(self) -> None:
        _require_string(self.motif_id, field_name="motif_id")
        if self.from_status not in _REVIEW_STATUSES:
            raise ValueError("from_status is not recognized")
        if self.to_status not in _REVIEW_STATUSES:
            raise ValueError("to_status is not recognized")

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "motif_id": self.motif_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "reviewer": self.reviewer,
            "reason": self.reason,
            "timestamp_utc": self.timestamp_utc,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9ReviewHistoryEntry:
        mapping = _require_mapping(value, field_name="review_history")
        return cls(
            motif_id=_require_string(mapping.get("motif_id"), field_name="motif_id"),
            from_status=_require_string(mapping.get("from_status"), field_name="from_status"),
            to_status=_require_string(mapping.get("to_status"), field_name="to_status"),
            reviewer=str(mapping.get("reviewer", "")),
            reason=str(mapping.get("reason", "")),
            timestamp_utc=str(mapping.get("timestamp_utc", "")),
        )


@dataclass(frozen=True)
class GRC9DiscoveryManifest:
    source_artifacts: tuple[GRC9SourceArtifact, ...]
    run_scope: GRC9ManifestRunScope
    structure_hypotheses: tuple[GRC9StructureHypothesis, ...] = ()
    selectors: tuple[GRC9SelectorSpec, ...] = ()
    motifs: tuple[GRC9MotifRecord, ...] = ()
    review_history: tuple[GRC9ReviewHistoryEntry, ...] = ()
    manifest_version: str = GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION
    output_roots: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if self.manifest_version != GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION:
            raise ValueError(
                "manifest_version must be "
                f"{GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION!r}"
            )

    def to_mapping(self) -> Mapping[str, Any]:
        payload: dict[str, Any] = {
            "manifest_version": self.manifest_version,
            "source_artifacts": [item.to_mapping() for item in self.source_artifacts],
            "run_scope": self.run_scope.to_mapping(),
            "structure_hypotheses": [
                item.to_mapping() for item in self.structure_hypotheses
            ],
            "selectors": [item.to_mapping() for item in self.selectors],
            "motifs": [item.to_mapping() for item in self.motifs],
            "review_history": [item.to_mapping() for item in self.review_history],
            "output_roots": dict(
                self.output_roots
                or {
                    "discovery": DISCOVERY_OUTPUT_ROOT,
                    "sessions": DISCOVERY_SESSION_ROOT,
                }
            ),
        }
        return payload

    def add_motif(self, motif: GRC9MotifRecord) -> GRC9DiscoveryManifest:
        if any(existing.motif_id == motif.motif_id for existing in self.motifs):
            raise ValueError(f"duplicate motif_id {motif.motif_id!r}")
        return replace(self, motifs=(*self.motifs, motif))

    def update_motif(self, motif_id: str, **updates: Any) -> GRC9DiscoveryManifest:
        _require_string(motif_id, field_name="motif_id")
        updated: list[GRC9MotifRecord] = []
        found = False
        for motif in self.motifs:
            if motif.motif_id != motif_id:
                updated.append(motif)
                continue
            found = True
            updated.append(replace(motif, **updates))
        if not found:
            raise ValueError(f"motif_id {motif_id!r} not found")
        return replace(self, motifs=tuple(updated))

    def add_review_history(
        self,
        entry: GRC9ReviewHistoryEntry,
    ) -> GRC9DiscoveryManifest:
        return replace(self, review_history=(*self.review_history, entry))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> GRC9DiscoveryManifest:
        mapping = _require_mapping(value, field_name="manifest")
        return cls(
            manifest_version=_require_string(
                mapping.get("manifest_version", GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION),
                field_name="manifest_version",
            ),
            source_artifacts=tuple(
                GRC9SourceArtifact.from_mapping(_require_mapping(item, field_name="source_artifacts[]"))
                for item in _require_sequence(mapping.get("source_artifacts", []), field_name="source_artifacts")
            ),
            run_scope=GRC9ManifestRunScope.from_mapping(
                _require_mapping(mapping.get("run_scope", {}), field_name="run_scope")
            ),
            structure_hypotheses=tuple(
                GRC9StructureHypothesis.from_mapping(
                    _require_mapping(item, field_name="structure_hypotheses[]")
                )
                for item in _require_sequence(
                    mapping.get("structure_hypotheses", []),
                    field_name="structure_hypotheses",
                )
            ),
            selectors=tuple(
                GRC9SelectorSpec.from_mapping(_require_mapping(item, field_name="selectors[]"))
                for item in _require_sequence(mapping.get("selectors", []), field_name="selectors")
            ),
            motifs=tuple(
                GRC9MotifRecord.from_mapping(_require_mapping(item, field_name="motifs[]"))
                for item in _require_sequence(mapping.get("motifs", []), field_name="motifs")
            ),
            review_history=tuple(
                GRC9ReviewHistoryEntry.from_mapping(
                    _require_mapping(item, field_name="review_history[]")
                )
                for item in _require_sequence(
                    mapping.get("review_history", []),
                    field_name="review_history",
                )
            ),
            output_roots=dict(
                _require_mapping(
                    mapping.get(
                        "output_roots",
                        {"discovery": DISCOVERY_OUTPUT_ROOT, "sessions": DISCOVERY_SESSION_ROOT},
                    ),
                    field_name="output_roots",
                )
            ),
        )


__all__ = [
    "GRC9_DISCOVERY_FAMILY",
    "GRC9_DISCOVERY_PROGRAM",
    "GRC9_DISCOVERY_TRACK",
    "GRC9_PHENOMENOLOGY_DISCOVERY_MANIFEST_VERSION",
    "GRC9DiscoveryManifest",
    "GRC9EvidenceFields",
    "GRC9ManifestRunScope",
    "GRC9MotifRecord",
    "GRC9PredictedSignature",
    "GRC9ReviewHistoryEntry",
    "GRC9SelectorSpec",
    "GRC9SourceArtifact",
    "GRC9SourceReference",
    "GRC9StructureHypothesis",
    "generated_lane_name",
    "is_discovery_profile_name",
    "is_generated_lane_name",
    "is_session_id",
    "perturbation_lane_name",
    "profile_name",
]
