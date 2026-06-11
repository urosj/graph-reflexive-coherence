"""Motion inference extension contract for temporal runtime evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from pygrc.core import InvalidLandscapeSeedError, canonicalize_json_value

from .seed import LandscapePrimitive, LandscapeSeed


MOTION_INFERENCE_EXTENSION_NAMESPACE = "motion_inference"
MOTION_INFERENCE_CONTRACT_VERSION = "motion_inference_iter1_v1"

MOTION_INFERENCE_AUTHORITY = "observed"

MOTION_INFERENCE_KINDS: tuple[str, ...] = (
    "coherence",
    "representative",
    "identity",
    "boundary",
    "topological",
)

MOTION_INFERENCE_RELATIONSHIPS: tuple[str, ...] = (
    "stationary",
    "drifted",
    "walked",
    "split",
    "merged",
    "collapsed",
    "dissolved",
    "emerged",
    "ambiguous",
)

MOTION_INFERENCE_EVIDENCE_QUALITY: tuple[str, ...] = (
    "strong",
    "partial",
    "degraded",
    "missing_surface",
    "diagnostic_only",
)

MOTION_INFERENCE_RUNTIME_FAMILIES: tuple[str, ...] = (
    "grcv3",
    "grc9",
    "grc9v3",
)

MOTION_INFERENCE_CHECKPOINT_SPACING: tuple[str, ...] = (
    "regular",
    "irregular",
    "ordinal_only",
    "unknown",
)

MOTION_INFERENCE_CONFIDENCE_THRESHOLDS: Mapping[str, float] = {
    "strong": 0.80,
    "partial": 0.50,
    "degraded": 0.40,
    "diagnostic_only": 0.25,
}

_FORBIDDEN_RUNTIME_STATE_KEYS = frozenset(
    {
        "budget_state",
        "coherence_by_node",
        "conductance_by_edge",
        "edge_records",
        "edges",
        "event_history",
        "event_rows",
        "events",
        "flux_by_edge",
        "graph",
        "graph_checkpoint_index",
        "graph_state",
        "node_records",
        "nodes",
        "run_summary",
        "runtime_state",
        "state",
        "step_rows",
        "topology",
    }
)


def _require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise InvalidLandscapeSeedError(f"{context} must be a mapping")
    return value


def _require_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidLandscapeSeedError(f"{context} must be a non-empty string")
    return value


def _require_optional_string(value: Any, *, context: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, context=context)


def _require_int(value: Any, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidLandscapeSeedError(f"{context} must be an int")
    return value


def _require_optional_float(value: Any, *, context: str) -> float | None:
    if value is None:
        return None
    return _require_float(value, context=context)


def _require_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(f"{context} must be a float-compatible number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidLandscapeSeedError(f"{context} must be finite")
    return number


def _require_confidence(value: Any, *, context: str) -> float:
    confidence = _require_float(value, context=context)
    if not 0.0 <= confidence <= 1.0:
        raise InvalidLandscapeSeedError(f"{context} must be in [0, 1]")
    return confidence


def _require_string_sequence(value: Any, *, context: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise InvalidLandscapeSeedError(f"{context} must be a list of strings")
    return tuple(
        _require_string(item, context=f"{context}[{index}]")
        for index, item in enumerate(value)
    )


def _require_int_sequence(value: Any, *, context: str) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise InvalidLandscapeSeedError(f"{context} must be a list of ints")
    return tuple(
        _require_int(item, context=f"{context}[{index}]")
        for index, item in enumerate(value)
    )


def _require_step_window(value: Any, *, context: str) -> tuple[int, int]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes) or len(value) != 2:
        raise InvalidLandscapeSeedError(f"{context} must be [start_step, end_step]")
    start = _require_int(value[0], context=f"{context}[0]")
    end = _require_int(value[1], context=f"{context}[1]")
    if start < 0 or end < start:
        raise InvalidLandscapeSeedError(f"{context} must be a non-negative ordered step window")
    return (start, end)


def _require_choice(value: Any, *, choices: tuple[str, ...], context: str) -> str:
    item = _require_string(value, context=context)
    if item not in choices:
        raise InvalidLandscapeSeedError(f"{context} must be one of {list(choices)}")
    return item


def _validate_no_runtime_state_smuggling(value: Any, *, context: str) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            if not isinstance(key, str):
                raise InvalidLandscapeSeedError(f"{context} keys must be strings")
            if key in _FORBIDDEN_RUNTIME_STATE_KEYS:
                raise InvalidLandscapeSeedError(
                    f"{context}.{key} embeds runtime state; store artifact paths or ids instead"
                )
            _validate_no_runtime_state_smuggling(inner, context=f"{context}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for index, inner in enumerate(value):
            _validate_no_runtime_state_smuggling(inner, context=f"{context}[{index}]")


@dataclass(frozen=True)
class MotionCheckpointSpacing:
    """Checkpoint spacing metadata for one motion window."""

    spacing_mode: str
    step_deltas: tuple[int, ...] = ()
    time_deltas: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        _require_choice(
            self.spacing_mode,
            choices=MOTION_INFERENCE_CHECKPOINT_SPACING,
            context="checkpoint_spacing.spacing_mode",
        )
        for index, delta in enumerate(self.step_deltas):
            if _require_int(delta, context=f"checkpoint_spacing.step_deltas[{index}]") < 0:
                raise InvalidLandscapeSeedError("checkpoint_spacing.step_deltas must be non-negative")
        for index, delta in enumerate(self.time_deltas):
            if _require_float(delta, context=f"checkpoint_spacing.time_deltas[{index}]") < 0.0:
                raise InvalidLandscapeSeedError("checkpoint_spacing.time_deltas must be non-negative")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "spacing_mode": self.spacing_mode,
            "step_deltas": [int(value) for value in self.step_deltas],
            "time_deltas": [float(value) for value in self.time_deltas],
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionCheckpointSpacing":
        mapping = _require_mapping(value, context="checkpoint_spacing")
        return cls(
            spacing_mode=_require_choice(
                mapping.get("spacing_mode"),
                choices=MOTION_INFERENCE_CHECKPOINT_SPACING,
                context="checkpoint_spacing.spacing_mode",
            ),
            step_deltas=_require_int_sequence(
                mapping.get("step_deltas", ()),
                context="checkpoint_spacing.step_deltas",
            ),
            time_deltas=tuple(
                _require_float(item, context=f"checkpoint_spacing.time_deltas[{index}]")
                for index, item in enumerate(mapping.get("time_deltas", ()))
            ),
        )


@dataclass(frozen=True)
class MotionWindow:
    """Step/checkpoint window used for one motion report."""

    start_step: int
    end_step: int
    checkpoint_ids: tuple[str, ...]
    policy: str | None = None
    checkpoint_spacing: MotionCheckpointSpacing | None = None

    def __post_init__(self) -> None:
        if self.start_step < 0 or self.end_step < self.start_step:
            raise InvalidLandscapeSeedError("motion_window must be a non-negative ordered step window")
        _require_string_sequence(self.checkpoint_ids, context="motion_window.checkpoint_ids")
        if self.policy is not None:
            _require_string(self.policy, context="motion_window.policy")

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "start_step": int(self.start_step),
            "end_step": int(self.end_step),
            "checkpoint_ids": list(self.checkpoint_ids),
        }
        if self.policy is not None:
            payload["policy"] = self.policy
        if self.checkpoint_spacing is not None:
            payload["checkpoint_spacing"] = self.checkpoint_spacing.to_mapping()
        return payload

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionWindow":
        mapping = _require_mapping(value, context="motion_window")
        spacing = mapping.get("checkpoint_spacing")
        return cls(
            start_step=_require_int(mapping.get("start_step"), context="motion_window.start_step"),
            end_step=_require_int(mapping.get("end_step"), context="motion_window.end_step"),
            checkpoint_ids=_require_string_sequence(
                mapping.get("checkpoint_ids", ()),
                context="motion_window.checkpoint_ids",
            ),
            policy=_require_optional_string(mapping.get("policy"), context="motion_window.policy"),
            checkpoint_spacing=None if spacing is None else MotionCheckpointSpacing.from_mapping(spacing),
        )


@dataclass(frozen=True)
class MotionCarrierSet:
    """Compressed carrier references for old/new motion endpoints."""

    node_ids: tuple[int, ...] = ()
    basin_ids: tuple[str, ...] = ()
    edge_ids: tuple[int, ...] = ()
    path_ids: tuple[str, ...] = ()
    primitive_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_int_sequence(self.node_ids, context="carrier.node_ids")
        _require_string_sequence(self.basin_ids, context="carrier.basin_ids")
        _require_int_sequence(self.edge_ids, context="carrier.edge_ids")
        _require_string_sequence(self.path_ids, context="carrier.path_ids")
        _require_string_sequence(self.primitive_ids, context="carrier.primitive_ids")
        if not any((self.node_ids, self.basin_ids, self.edge_ids, self.path_ids, self.primitive_ids)):
            raise InvalidLandscapeSeedError("carrier set must reference at least one node/basin/edge/path/primitive")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "node_ids": [int(value) for value in self.node_ids],
            "basin_ids": list(self.basin_ids),
            "edge_ids": [int(value) for value in self.edge_ids],
            "path_ids": list(self.path_ids),
            "primitive_ids": list(self.primitive_ids),
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionCarrierSet":
        mapping = _require_mapping(value, context="carrier")
        return cls(
            node_ids=_require_int_sequence(mapping.get("node_ids", ()), context="carrier.node_ids"),
            basin_ids=_require_string_sequence(mapping.get("basin_ids", ()), context="carrier.basin_ids"),
            edge_ids=_require_int_sequence(mapping.get("edge_ids", ()), context="carrier.edge_ids"),
            path_ids=_require_string_sequence(mapping.get("path_ids", ()), context="carrier.path_ids"),
            primitive_ids=_require_string_sequence(
                mapping.get("primitive_ids", ()),
                context="carrier.primitive_ids",
            ),
        )


@dataclass(frozen=True)
class MotionEvidence:
    """Compressed evidence references for one motion record."""

    telemetry_fields: tuple[str, ...] = ()
    checkpoint_ids: tuple[str, ...] = ()
    step_ids: tuple[int, ...] = ()
    node_ids: tuple[int, ...] = ()
    edge_ids: tuple[int, ...] = ()
    path_node_ids: tuple[int, ...] = ()
    event_ids: tuple[str, ...] = ()
    budget_accountability: str | None = None
    degradation_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_string_sequence(self.telemetry_fields, context="motion_evidence.telemetry_fields")
        _require_string_sequence(self.checkpoint_ids, context="motion_evidence.checkpoint_ids")
        _require_int_sequence(self.step_ids, context="motion_evidence.step_ids")
        _require_int_sequence(self.node_ids, context="motion_evidence.node_ids")
        _require_int_sequence(self.edge_ids, context="motion_evidence.edge_ids")
        _require_int_sequence(self.path_node_ids, context="motion_evidence.path_node_ids")
        _require_string_sequence(self.event_ids, context="motion_evidence.event_ids")
        _require_string_sequence(self.degradation_reasons, context="motion_evidence.degradation_reasons")
        if self.budget_accountability is not None:
            _require_string(self.budget_accountability, context="motion_evidence.budget_accountability")
        if not any(
            (
                self.telemetry_fields,
                self.checkpoint_ids,
                self.step_ids,
                self.node_ids,
                self.edge_ids,
                self.path_node_ids,
                self.event_ids,
            )
        ):
            raise InvalidLandscapeSeedError("motion evidence must reference at least one runtime artifact surface")

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "telemetry_fields": list(self.telemetry_fields),
            "checkpoint_ids": list(self.checkpoint_ids),
            "step_ids": [int(value) for value in self.step_ids],
            "node_ids": [int(value) for value in self.node_ids],
            "edge_ids": [int(value) for value in self.edge_ids],
            "path_node_ids": [int(value) for value in self.path_node_ids],
            "event_ids": list(self.event_ids),
            "degradation_reasons": list(self.degradation_reasons),
        }
        if self.budget_accountability is not None:
            payload["budget_accountability"] = self.budget_accountability
        return payload

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionEvidence":
        _validate_no_runtime_state_smuggling(value, context="motion_evidence")
        mapping = _require_mapping(value, context="motion_evidence")
        return cls(
            telemetry_fields=_require_string_sequence(
                mapping.get("telemetry_fields", ()),
                context="motion_evidence.telemetry_fields",
            ),
            checkpoint_ids=_require_string_sequence(
                mapping.get("checkpoint_ids", ()),
                context="motion_evidence.checkpoint_ids",
            ),
            step_ids=_require_int_sequence(mapping.get("step_ids", ()), context="motion_evidence.step_ids"),
            node_ids=_require_int_sequence(mapping.get("node_ids", ()), context="motion_evidence.node_ids"),
            edge_ids=_require_int_sequence(mapping.get("edge_ids", ()), context="motion_evidence.edge_ids"),
            path_node_ids=_require_int_sequence(
                mapping.get("path_node_ids", ()),
                context="motion_evidence.path_node_ids",
            ),
            event_ids=_require_string_sequence(mapping.get("event_ids", ()), context="motion_evidence.event_ids"),
            budget_accountability=_require_optional_string(
                mapping.get("budget_accountability"),
                context="motion_evidence.budget_accountability",
            ),
            degradation_reasons=_require_string_sequence(
                mapping.get("degradation_reasons", ()),
                context="motion_evidence.degradation_reasons",
            ),
        )


@dataclass(frozen=True)
class MotionCompetingClaim:
    """A weaker or conflicting interpretation considered by a classifier."""

    relationship: str
    confidence: float
    reason: str
    classifier_id: str | None = None

    def __post_init__(self) -> None:
        _require_choice(
            self.relationship,
            choices=MOTION_INFERENCE_RELATIONSHIPS,
            context="competing_claim.relationship",
        )
        _require_confidence(self.confidence, context="competing_claim.confidence")
        _require_string(self.reason, context="competing_claim.reason")
        if self.classifier_id is not None:
            _require_string(self.classifier_id, context="competing_claim.classifier_id")

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "relationship": self.relationship,
            "confidence": float(self.confidence),
            "reason": self.reason,
        }
        if self.classifier_id is not None:
            payload["classifier_id"] = self.classifier_id
        return payload

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionCompetingClaim":
        mapping = _require_mapping(value, context="competing_claim")
        return cls(
            relationship=_require_choice(
                mapping.get("relationship"),
                choices=MOTION_INFERENCE_RELATIONSHIPS,
                context="competing_claim.relationship",
            ),
            confidence=_require_confidence(mapping.get("confidence"), context="competing_claim.confidence"),
            reason=_require_string(mapping.get("reason"), context="competing_claim.reason"),
            classifier_id=_require_optional_string(
                mapping.get("classifier_id"),
                context="competing_claim.classifier_id",
            ),
        )


@dataclass(frozen=True)
class MotionRecord:
    """One inferred temporal motion relationship."""

    motion_id: str
    classifier_id: str
    classifier_version: str
    motion_kind: str
    relationship: str
    confidence: float
    evidence_quality: str
    source_runtime_family: str
    step_window: tuple[int, int]
    step_ids: tuple[int, ...]
    old_carriers: MotionCarrierSet
    new_carriers: MotionCarrierSet
    evidence: MotionEvidence
    transferred_mass: float | None = None
    competing_claims: tuple[MotionCompetingClaim, ...] = ()
    non_claims: tuple[str, ...] = ()
    authority: str = MOTION_INFERENCE_AUTHORITY
    contract_version: str = MOTION_INFERENCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != MOTION_INFERENCE_CONTRACT_VERSION:
            raise InvalidLandscapeSeedError("motion_record.contract_version is unsupported")
        if self.authority != MOTION_INFERENCE_AUTHORITY:
            raise InvalidLandscapeSeedError("motion_record.authority must be observed")
        _require_string(self.motion_id, context="motion_record.motion_id")
        _require_string(self.classifier_id, context="motion_record.classifier_id")
        _require_string(self.classifier_version, context="motion_record.classifier_version")
        _require_choice(
            self.motion_kind,
            choices=MOTION_INFERENCE_KINDS,
            context="motion_record.motion_kind",
        )
        _require_choice(
            self.relationship,
            choices=MOTION_INFERENCE_RELATIONSHIPS,
            context="motion_record.relationship",
        )
        _require_confidence(self.confidence, context="motion_record.confidence")
        _require_choice(
            self.evidence_quality,
            choices=MOTION_INFERENCE_EVIDENCE_QUALITY,
            context="motion_record.evidence_quality",
        )
        _require_choice(
            self.source_runtime_family,
            choices=MOTION_INFERENCE_RUNTIME_FAMILIES,
            context="motion_record.source_runtime_family",
        )
        _require_step_window(self.step_window, context="motion_record.step_window")
        _require_int_sequence(self.step_ids, context="motion_record.step_ids")
        if not self.step_ids:
            raise InvalidLandscapeSeedError("motion_record.step_ids must not be empty")
        for claim in self.competing_claims:
            if not isinstance(claim, MotionCompetingClaim):
                raise InvalidLandscapeSeedError("motion_record.competing_claims must contain MotionCompetingClaim")
        _require_string_sequence(self.non_claims, context="motion_record.non_claims")
        _require_optional_float(self.transferred_mass, context="motion_record.transferred_mass")
        if self.transferred_mass is not None and self.transferred_mass < 0.0:
            raise InvalidLandscapeSeedError("motion_record.transferred_mass must be non-negative")
        if self.motion_kind == "identity" and self.relationship != "stationary" and not self.competing_claims:
            raise InvalidLandscapeSeedError(
                "non-stationary identity motion records must include competing_claims, even if empty alternatives were rejected"
            )

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "motion_id": self.motion_id,
            "authority": self.authority,
            "classifier_id": self.classifier_id,
            "classifier_version": self.classifier_version,
            "motion_kind": self.motion_kind,
            "relationship": self.relationship,
            "confidence": float(self.confidence),
            "evidence_quality": self.evidence_quality,
            "source_runtime_family": self.source_runtime_family,
            "step_window": [int(self.step_window[0]), int(self.step_window[1])],
            "step_ids": [int(value) for value in self.step_ids],
            "old_carriers": self.old_carriers.to_mapping(),
            "new_carriers": self.new_carriers.to_mapping(),
            "evidence": self.evidence.to_mapping(),
            "competing_claims": [claim.to_mapping() for claim in self.competing_claims],
            "non_claims": list(self.non_claims),
        }
        if self.transferred_mass is not None:
            payload["transferred_mass"] = float(self.transferred_mass)
        return payload

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionRecord":
        _validate_no_runtime_state_smuggling(value, context="motion_record")
        mapping = _require_mapping(value, context="motion_record")
        return cls(
            contract_version=_require_string(
                mapping.get("contract_version"),
                context="motion_record.contract_version",
            ),
            motion_id=_require_string(mapping.get("motion_id"), context="motion_record.motion_id"),
            authority=_require_choice(
                mapping.get("authority"),
                choices=(MOTION_INFERENCE_AUTHORITY,),
                context="motion_record.authority",
            ),
            classifier_id=_require_string(
                mapping.get("classifier_id"),
                context="motion_record.classifier_id",
            ),
            classifier_version=_require_string(
                mapping.get("classifier_version"),
                context="motion_record.classifier_version",
            ),
            motion_kind=_require_choice(
                mapping.get("motion_kind"),
                choices=MOTION_INFERENCE_KINDS,
                context="motion_record.motion_kind",
            ),
            relationship=_require_choice(
                mapping.get("relationship"),
                choices=MOTION_INFERENCE_RELATIONSHIPS,
                context="motion_record.relationship",
            ),
            confidence=_require_confidence(mapping.get("confidence"), context="motion_record.confidence"),
            evidence_quality=_require_choice(
                mapping.get("evidence_quality"),
                choices=MOTION_INFERENCE_EVIDENCE_QUALITY,
                context="motion_record.evidence_quality",
            ),
            source_runtime_family=_require_choice(
                mapping.get("source_runtime_family"),
                choices=MOTION_INFERENCE_RUNTIME_FAMILIES,
                context="motion_record.source_runtime_family",
            ),
            step_window=_require_step_window(mapping.get("step_window"), context="motion_record.step_window"),
            step_ids=_require_int_sequence(mapping.get("step_ids", ()), context="motion_record.step_ids"),
            old_carriers=MotionCarrierSet.from_mapping(mapping.get("old_carriers")),
            new_carriers=MotionCarrierSet.from_mapping(mapping.get("new_carriers")),
            evidence=MotionEvidence.from_mapping(mapping.get("evidence")),
            transferred_mass=_require_optional_float(
                mapping.get("transferred_mass"),
                context="motion_record.transferred_mass",
            ),
            competing_claims=tuple(
                MotionCompetingClaim.from_mapping(item)
                for item in mapping.get("competing_claims", ())
            ),
            non_claims=_require_string_sequence(
                mapping.get("non_claims", ()),
                context="motion_record.non_claims",
            ),
        )


@dataclass(frozen=True)
class MotionReport:
    """Top-level motion inference report."""

    source_session_id: str
    source_runtime_family: str
    source_artifact_paths: tuple[str, ...]
    motion_window: MotionWindow
    records: tuple[MotionRecord, ...] = ()
    contract_version: str = MOTION_INFERENCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != MOTION_INFERENCE_CONTRACT_VERSION:
            raise InvalidLandscapeSeedError("motion_report.contract_version is unsupported")
        _require_string(self.source_session_id, context="motion_report.source_session_id")
        _require_choice(
            self.source_runtime_family,
            choices=MOTION_INFERENCE_RUNTIME_FAMILIES,
            context="motion_report.source_runtime_family",
        )
        _require_string_sequence(
            self.source_artifact_paths,
            context="motion_report.source_artifact_paths",
        )
        for record in self.records:
            if not isinstance(record, MotionRecord):
                raise InvalidLandscapeSeedError("motion_report.records must contain MotionRecord")
            if record.source_runtime_family != self.source_runtime_family:
                raise InvalidLandscapeSeedError("motion_report records must match source_runtime_family")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "source_session_id": self.source_session_id,
            "source_runtime_family": self.source_runtime_family,
            "source_artifact_paths": list(self.source_artifact_paths),
            "motion_window": self.motion_window.to_mapping(),
            "records": [record.to_mapping() for record in self.records],
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionReport":
        _validate_no_runtime_state_smuggling(value, context="motion_report")
        mapping = _require_mapping(value, context="motion_report")
        return cls(
            contract_version=_require_string(
                mapping.get("contract_version"),
                context="motion_report.contract_version",
            ),
            source_session_id=_require_string(
                mapping.get("source_session_id"),
                context="motion_report.source_session_id",
            ),
            source_runtime_family=_require_choice(
                mapping.get("source_runtime_family"),
                choices=MOTION_INFERENCE_RUNTIME_FAMILIES,
                context="motion_report.source_runtime_family",
            ),
            source_artifact_paths=_require_string_sequence(
                mapping.get("source_artifact_paths", ()),
                context="motion_report.source_artifact_paths",
            ),
            motion_window=MotionWindow.from_mapping(mapping.get("motion_window")),
            records=tuple(
                MotionRecord.from_mapping(item)
                for item in mapping.get("records", ())
            ),
        )


@dataclass(frozen=True)
class MotionPrimitiveExtension:
    """Primitive-level `primitive.extensions.motion_inference` reference."""

    motion_id: str
    motion_kind: str
    relationship: str
    source_window: tuple[int, int]
    confidence: float
    authority: str = MOTION_INFERENCE_AUTHORITY
    contract_version: str = MOTION_INFERENCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != MOTION_INFERENCE_CONTRACT_VERSION:
            raise InvalidLandscapeSeedError("primitive motion_inference.contract_version is unsupported")
        if self.authority != MOTION_INFERENCE_AUTHORITY:
            raise InvalidLandscapeSeedError("primitive motion_inference.authority must be observed")
        _require_string(self.motion_id, context="primitive.motion_inference.motion_id")
        _require_choice(
            self.motion_kind,
            choices=MOTION_INFERENCE_KINDS,
            context="primitive.motion_inference.motion_kind",
        )
        _require_choice(
            self.relationship,
            choices=MOTION_INFERENCE_RELATIONSHIPS,
            context="primitive.motion_inference.relationship",
        )
        _require_step_window(self.source_window, context="primitive.motion_inference.source_window")
        _require_confidence(self.confidence, context="primitive.motion_inference.confidence")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "authority": self.authority,
            "motion_id": self.motion_id,
            "motion_kind": self.motion_kind,
            "relationship": self.relationship,
            "source_window": [int(self.source_window[0]), int(self.source_window[1])],
            "confidence": float(self.confidence),
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "MotionPrimitiveExtension":
        _validate_no_runtime_state_smuggling(value, context="primitive.motion_inference")
        mapping = _require_mapping(value, context="primitive.motion_inference")
        return cls(
            contract_version=_require_string(
                mapping.get("contract_version"),
                context="primitive.motion_inference.contract_version",
            ),
            authority=_require_choice(
                mapping.get("authority"),
                choices=(MOTION_INFERENCE_AUTHORITY,),
                context="primitive.motion_inference.authority",
            ),
            motion_id=_require_string(
                mapping.get("motion_id"),
                context="primitive.motion_inference.motion_id",
            ),
            motion_kind=_require_choice(
                mapping.get("motion_kind"),
                choices=MOTION_INFERENCE_KINDS,
                context="primitive.motion_inference.motion_kind",
            ),
            relationship=_require_choice(
                mapping.get("relationship"),
                choices=MOTION_INFERENCE_RELATIONSHIPS,
                context="primitive.motion_inference.relationship",
            ),
            source_window=_require_step_window(
                mapping.get("source_window"),
                context="primitive.motion_inference.source_window",
            ),
            confidence=_require_confidence(
                mapping.get("confidence"),
                context="primitive.motion_inference.confidence",
            ),
        )


def motion_report_mapping(report: MotionReport) -> dict[str, Any]:
    """Return a deterministic JSON-safe motion report mapping."""

    return canonicalize_json_value(report.to_mapping())


def motion_record_mapping(record: MotionRecord) -> dict[str, Any]:
    """Return a deterministic JSON-safe motion record mapping."""

    return canonicalize_json_value(record.to_mapping())


def motion_primitive_extension_mapping(extension: MotionPrimitiveExtension) -> dict[str, Any]:
    """Return a deterministic JSON-safe primitive motion extension mapping."""

    return canonicalize_json_value(extension.to_mapping())


def validate_motion_primitive_extension(primitive: LandscapePrimitive) -> None:
    """Validate one primitive-level motion extension when present."""

    payload = primitive.extensions.get(MOTION_INFERENCE_EXTENSION_NAMESPACE)
    if payload is None:
        return
    MotionPrimitiveExtension.from_mapping(payload)


def validate_motion_seed_extensions(seed: LandscapeSeed) -> None:
    """Validate motion extensions embedded in one `LandscapeSeed`."""

    top_level = seed.extensions.get(MOTION_INFERENCE_EXTENSION_NAMESPACE)
    if top_level is not None:
        _validate_no_runtime_state_smuggling(top_level, context="motion_inference")
        mapping = _require_mapping(top_level, context="motion_inference")
        if "motion_record_ids" in mapping:
            _require_string_sequence(
                mapping.get("motion_record_ids", ()),
                context="motion_inference.motion_record_ids",
            )
        if "contract_version" in mapping:
            contract_version = _require_string(
                mapping.get("contract_version"),
                context="motion_inference.contract_version",
            )
            if contract_version != MOTION_INFERENCE_CONTRACT_VERSION:
                raise InvalidLandscapeSeedError("motion_inference.contract_version is unsupported")
    for primitive in seed.primitives:
        validate_motion_primitive_extension(primitive)


__all__ = [
    "MOTION_INFERENCE_AUTHORITY",
    "MOTION_INFERENCE_CHECKPOINT_SPACING",
    "MOTION_INFERENCE_CONFIDENCE_THRESHOLDS",
    "MOTION_INFERENCE_CONTRACT_VERSION",
    "MOTION_INFERENCE_EVIDENCE_QUALITY",
    "MOTION_INFERENCE_EXTENSION_NAMESPACE",
    "MOTION_INFERENCE_KINDS",
    "MOTION_INFERENCE_RELATIONSHIPS",
    "MOTION_INFERENCE_RUNTIME_FAMILIES",
    "MotionCarrierSet",
    "MotionCheckpointSpacing",
    "MotionCompetingClaim",
    "MotionEvidence",
    "MotionPrimitiveExtension",
    "MotionRecord",
    "MotionReport",
    "MotionWindow",
    "motion_primitive_extension_mapping",
    "motion_record_mapping",
    "motion_report_mapping",
    "validate_motion_primitive_extension",
    "validate_motion_seed_extensions",
]
