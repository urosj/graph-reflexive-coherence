"""Landscape inference extension contract for observed runtime geometry."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from pygrc.core import InvalidLandscapeSeedError, canonicalize_json_value

from .seed import LandscapePrimitive, LandscapeSeed


LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE = "landscape_inference"
LANDSCAPE_INFERENCE_CONTRACT_VERSION = "landscape_inference_iter1_v1"

LANDSCAPE_INFERENCE_AUTHORITIES: tuple[str, ...] = (
    "authored",
    "lowered",
    "observed",
)

LANDSCAPE_INFERENCE_RELATIONSHIPS: tuple[str, ...] = (
    "preserved",
    "transformed",
    "split",
    "collapsed",
    "emerged",
    "dissolved",
    "unknown",
)

LANDSCAPE_INFERENCE_RUNTIME_FAMILIES: tuple[str, ...] = (
    "grcv3",
    "grc9",
    "grc9v3",
)

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


def _require_float(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise InvalidLandscapeSeedError(f"{context} must be a float-compatible number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidLandscapeSeedError(f"{context} must be finite")
    return number


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
class LandscapeInferenceWindow:
    """Step window used to infer one observed landscape."""

    start_step: int
    end_step: int
    policy: str | None = None

    def __post_init__(self) -> None:
        if self.start_step < 0 or self.end_step < self.start_step:
            raise InvalidLandscapeSeedError("inference_window must be a non-negative ordered step window")
        if self.policy is not None:
            _require_string(self.policy, context="inference_window.policy")

    def to_mapping(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "start_step": int(self.start_step),
            "end_step": int(self.end_step),
        }
        if self.policy is not None:
            payload["policy"] = self.policy
        return payload

    @classmethod
    def from_mapping(cls, value: Any) -> "LandscapeInferenceWindow":
        mapping = _require_mapping(value, context="inference_window")
        return cls(
            start_step=_require_int(mapping.get("start_step"), context="inference_window.start_step"),
            end_step=_require_int(mapping.get("end_step"), context="inference_window.end_step"),
            policy=_require_optional_string(mapping.get("policy"), context="inference_window.policy"),
        )


@dataclass(frozen=True)
class LandscapeInferenceObservedFrom:
    """Runtime artifact provenance for one observed primitive."""

    session_id: str
    run_id: str
    artifact_root: str
    step_window: tuple[int, int]

    def __post_init__(self) -> None:
        _require_string(self.session_id, context="observed_from.session_id")
        _require_string(self.run_id, context="observed_from.run_id")
        _require_string(self.artifact_root, context="observed_from.artifact_root")
        _require_step_window(self.step_window, context="observed_from.step_window")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "run_id": self.run_id,
            "artifact_root": self.artifact_root,
            "step_window": [int(self.step_window[0]), int(self.step_window[1])],
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "LandscapeInferenceObservedFrom":
        mapping = _require_mapping(value, context="observed_from")
        return cls(
            session_id=_require_string(mapping.get("session_id"), context="observed_from.session_id"),
            run_id=_require_string(mapping.get("run_id"), context="observed_from.run_id"),
            artifact_root=_require_string(mapping.get("artifact_root"), context="observed_from.artifact_root"),
            step_window=_require_step_window(mapping.get("step_window"), context="observed_from.step_window"),
        )


@dataclass(frozen=True)
class LandscapeInferenceEvidence:
    """Compressed evidence references for one inferred primitive."""

    telemetry_fields: tuple[str, ...] = ()
    checkpoint_ids: tuple[str, ...] = ()
    node_ids: tuple[int, ...] = ()
    edge_ids: tuple[int, ...] = ()
    path_node_ids: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _require_string_sequence(self.telemetry_fields, context="evidence.telemetry_fields")
        _require_string_sequence(self.checkpoint_ids, context="evidence.checkpoint_ids")
        _require_int_sequence(self.node_ids, context="evidence.node_ids")
        _require_int_sequence(self.edge_ids, context="evidence.edge_ids")
        _require_int_sequence(self.path_node_ids, context="evidence.path_node_ids")
        if not any(
            (
                self.telemetry_fields,
                self.checkpoint_ids,
                self.node_ids,
                self.edge_ids,
                self.path_node_ids,
            )
        ):
            raise InvalidLandscapeSeedError("evidence must reference at least one telemetry/checkpoint/node/edge surface")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "telemetry_fields": list(self.telemetry_fields),
            "checkpoint_ids": list(self.checkpoint_ids),
            "node_ids": [int(item) for item in self.node_ids],
            "edge_ids": [int(item) for item in self.edge_ids],
            "path_node_ids": [int(item) for item in self.path_node_ids],
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "LandscapeInferenceEvidence":
        mapping = _require_mapping(value, context="evidence")
        return cls(
            telemetry_fields=_require_string_sequence(
                mapping.get("telemetry_fields", ()),
                context="evidence.telemetry_fields",
            ),
            checkpoint_ids=_require_string_sequence(
                mapping.get("checkpoint_ids", ()),
                context="evidence.checkpoint_ids",
            ),
            node_ids=_require_int_sequence(mapping.get("node_ids", ()), context="evidence.node_ids"),
            edge_ids=_require_int_sequence(mapping.get("edge_ids", ()), context="evidence.edge_ids"),
            path_node_ids=_require_int_sequence(
                mapping.get("path_node_ids", ()),
                context="evidence.path_node_ids",
            ),
        )


@dataclass(frozen=True)
class LandscapeInferenceTopLevelExtension:
    """Top-level `seed.extensions.landscape_inference` contract."""

    source_session_id: str
    source_artifact_paths: tuple[str, ...]
    inference_window: LandscapeInferenceWindow
    source_runtime_family: str
    contract_version: str = LANDSCAPE_INFERENCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != LANDSCAPE_INFERENCE_CONTRACT_VERSION:
            raise InvalidLandscapeSeedError("landscape_inference.contract_version is unsupported")
        _require_string(self.source_session_id, context="landscape_inference.source_session_id")
        _require_string_sequence(
            self.source_artifact_paths,
            context="landscape_inference.source_artifact_paths",
        )
        _require_choice(
            self.source_runtime_family,
            choices=LANDSCAPE_INFERENCE_RUNTIME_FAMILIES,
            context="landscape_inference.source_runtime_family",
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "source_session_id": self.source_session_id,
            "source_artifact_paths": list(self.source_artifact_paths),
            "source_runtime_family": self.source_runtime_family,
            "inference_window": self.inference_window.to_mapping(),
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "LandscapeInferenceTopLevelExtension":
        _validate_no_runtime_state_smuggling(value, context="landscape_inference")
        mapping = _require_mapping(value, context="landscape_inference")
        return cls(
            contract_version=_require_string(
                mapping.get("contract_version"),
                context="landscape_inference.contract_version",
            ),
            source_session_id=_require_string(
                mapping.get("source_session_id"),
                context="landscape_inference.source_session_id",
            ),
            source_artifact_paths=_require_string_sequence(
                mapping.get("source_artifact_paths", ()),
                context="landscape_inference.source_artifact_paths",
            ),
            source_runtime_family=_require_choice(
                mapping.get("source_runtime_family"),
                choices=LANDSCAPE_INFERENCE_RUNTIME_FAMILIES,
                context="landscape_inference.source_runtime_family",
            ),
            inference_window=LandscapeInferenceWindow.from_mapping(
                mapping.get("inference_window")
            ),
        )


@dataclass(frozen=True)
class LandscapeInferencePrimitiveExtension:
    """Primitive-level `primitive.extensions.landscape_inference` contract."""

    authority: str
    classifier_id: str
    classifier_version: str
    confidence: float
    source_runtime_family: str
    observed_from: LandscapeInferenceObservedFrom
    evidence: LandscapeInferenceEvidence
    relationship_to_authored: str
    matched_authored_primitive_id: str | None = None
    contract_version: str = LANDSCAPE_INFERENCE_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != LANDSCAPE_INFERENCE_CONTRACT_VERSION:
            raise InvalidLandscapeSeedError("primitive landscape_inference.contract_version is unsupported")
        _require_choice(
            self.authority,
            choices=LANDSCAPE_INFERENCE_AUTHORITIES,
            context="primitive.landscape_inference.authority",
        )
        _require_string(self.classifier_id, context="primitive.landscape_inference.classifier_id")
        _require_string(
            self.classifier_version,
            context="primitive.landscape_inference.classifier_version",
        )
        confidence = _require_float(
            self.confidence,
            context="primitive.landscape_inference.confidence",
        )
        if not 0.0 <= confidence <= 1.0:
            raise InvalidLandscapeSeedError("primitive.landscape_inference.confidence must be in [0, 1]")
        _require_choice(
            self.source_runtime_family,
            choices=LANDSCAPE_INFERENCE_RUNTIME_FAMILIES,
            context="primitive.landscape_inference.source_runtime_family",
        )
        _require_choice(
            self.relationship_to_authored,
            choices=LANDSCAPE_INFERENCE_RELATIONSHIPS,
            context="primitive.landscape_inference.relationship_to_authored",
        )
        if self.matched_authored_primitive_id is not None:
            _require_string(
                self.matched_authored_primitive_id,
                context="primitive.landscape_inference.matched_authored_primitive_id",
            )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "authority": self.authority,
            "classifier_id": self.classifier_id,
            "classifier_version": self.classifier_version,
            "confidence": float(self.confidence),
            "source_runtime_family": self.source_runtime_family,
            "observed_from": self.observed_from.to_mapping(),
            "evidence": self.evidence.to_mapping(),
            "matched_authored_primitive_id": self.matched_authored_primitive_id,
            "relationship_to_authored": self.relationship_to_authored,
        }

    @classmethod
    def from_mapping(cls, value: Any) -> "LandscapeInferencePrimitiveExtension":
        _validate_no_runtime_state_smuggling(value, context="primitive.landscape_inference")
        mapping = _require_mapping(value, context="primitive.landscape_inference")
        return cls(
            contract_version=_require_string(
                mapping.get("contract_version"),
                context="primitive.landscape_inference.contract_version",
            ),
            authority=_require_choice(
                mapping.get("authority"),
                choices=LANDSCAPE_INFERENCE_AUTHORITIES,
                context="primitive.landscape_inference.authority",
            ),
            classifier_id=_require_string(
                mapping.get("classifier_id"),
                context="primitive.landscape_inference.classifier_id",
            ),
            classifier_version=_require_string(
                mapping.get("classifier_version"),
                context="primitive.landscape_inference.classifier_version",
            ),
            confidence=_require_float(
                mapping.get("confidence"),
                context="primitive.landscape_inference.confidence",
            ),
            source_runtime_family=_require_choice(
                mapping.get("source_runtime_family"),
                choices=LANDSCAPE_INFERENCE_RUNTIME_FAMILIES,
                context="primitive.landscape_inference.source_runtime_family",
            ),
            observed_from=LandscapeInferenceObservedFrom.from_mapping(mapping.get("observed_from")),
            evidence=LandscapeInferenceEvidence.from_mapping(mapping.get("evidence")),
            matched_authored_primitive_id=_require_optional_string(
                mapping.get("matched_authored_primitive_id"),
                context="primitive.landscape_inference.matched_authored_primitive_id",
            ),
            relationship_to_authored=_require_choice(
                mapping.get("relationship_to_authored"),
                choices=LANDSCAPE_INFERENCE_RELATIONSHIPS,
                context="primitive.landscape_inference.relationship_to_authored",
            ),
        )


def landscape_inference_top_level_mapping(
    extension: LandscapeInferenceTopLevelExtension,
) -> dict[str, Any]:
    """Return a deterministic JSON-safe top-level extension mapping."""

    return canonicalize_json_value(extension.to_mapping())


def landscape_inference_primitive_mapping(
    extension: LandscapeInferencePrimitiveExtension,
) -> dict[str, Any]:
    """Return a deterministic JSON-safe primitive extension mapping."""

    return canonicalize_json_value(extension.to_mapping())


def validate_landscape_inference_seed_extensions(seed: LandscapeSeed) -> None:
    """Validate landscape-inference extensions embedded in one `LandscapeSeed`."""

    top_level = seed.extensions.get(LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE)
    if top_level is not None:
        LandscapeInferenceTopLevelExtension.from_mapping(top_level)
    for primitive in seed.primitives:
        validate_landscape_inference_primitive_extension(primitive)


def validate_landscape_inference_primitive_extension(primitive: LandscapePrimitive) -> None:
    """Validate one primitive-level landscape-inference extension when present."""

    payload = primitive.extensions.get(LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE)
    if payload is None:
        return
    LandscapeInferencePrimitiveExtension.from_mapping(payload)


__all__ = [
    "LANDSCAPE_INFERENCE_AUTHORITIES",
    "LANDSCAPE_INFERENCE_CONTRACT_VERSION",
    "LANDSCAPE_INFERENCE_EXTENSION_NAMESPACE",
    "LANDSCAPE_INFERENCE_RELATIONSHIPS",
    "LANDSCAPE_INFERENCE_RUNTIME_FAMILIES",
    "LandscapeInferenceEvidence",
    "LandscapeInferenceObservedFrom",
    "LandscapeInferencePrimitiveExtension",
    "LandscapeInferenceTopLevelExtension",
    "LandscapeInferenceWindow",
    "landscape_inference_primitive_mapping",
    "landscape_inference_top_level_mapping",
    "validate_landscape_inference_primitive_extension",
    "validate_landscape_inference_seed_extensions",
]
