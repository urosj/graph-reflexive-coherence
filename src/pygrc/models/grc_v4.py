"""Generic V4 request boundary; no executable GRCV4 facade or support claims.

Step input shape is weaker than the strict operation request. Migration
records are declarations only: decoding cannot resolve profiles, authenticate
live state or admit a crossing. No topology events, harness hooks, pickle or
state restoration are accepted through this request surface.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import ClassVar, Literal, Self, TypeVar

from .grc_v4_codec import (
    V4SchemaError, canonical_json_bytes, decode_canonical_json, decode_record_payload,
)
from .grc_v4_profile import _Record
from .grc_v4_state import FrozenJSONMap

_T = TypeVar("_T", bound=_Record)


def _nested_record(value: object, kind: type[_T]) -> _T:
    """Detach and revalidate even an already-typed nested configuration."""
    if type(value) is kind:
        assert isinstance(value, _Record)
        return kind.from_payload(value.to_payload())
    if isinstance(value, Mapping):
        return kind.from_payload(value)
    raise V4SchemaError(f"expected {kind.__name__} or its primitive payload")


@dataclass(frozen=True, slots=True, eq=False)
class _StepRequestRecord(_Record):
    schema_version: str
    operation_id: str
    dt: float
    context_value: FrozenJSONMap
    boundary_input: FrozenJSONMap | None = None
    external_source: FrozenJSONMap | None = None

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        # Copy/domain validation precedes numeric normalization. Native unsafe
        # integers, bools, nonfinite values and negative zero cannot be coerced.
        object.__setattr__(self, "dt", float(self.dt))

    def to_canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_canonical_bytes(cls, data: bytes | str) -> Self:
        return cls.from_payload(decode_canonical_json(data))


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4StepRequestInput(_StepRequestRecord):
    """Shape-valid external input; negative duration can reach admission."""

    SCHEMA: ClassVar[str] = "step_request_input"
    schema_version: Literal["grcv4-step-request-input-v1"]


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4StepRequest(_StepRequestRecord):
    """Strict nonnegative request; not proof of live state/domain admission."""

    SCHEMA: ClassVar[str] = "step_request"
    schema_version: Literal["grcv4-step-request-v1"]


def decode_step_request_input(
    data: bytes | str, *,
    encoding: Literal["configuration", "canonical"] = "configuration",
) -> GRCV4StepRequestInput:
    """Decode configuration JSON by default, not live-state admission.

    Configuration accepts finite binary64 decimal/exponent tokens (including
    5e-324 and 1e308), but integer-shaped tokens must be safe integers. Use
    encoding="canonical" for exact JCS bytes from to_canonical_bytes(), whose
    large binary64 values may serialize as oversized integer-shaped tokens.
    Canonical reconstruction requires byte-exact JCS; it is not an automatic
    retry for rejected configuration. Both routes reject nonzero underflow.
    """
    payload = decode_record_payload("step_request_input", data, encoding=encoding)
    return GRCV4StepRequestInput.from_payload(payload)


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4MigrationPolicy(_Record):
    SCHEMA: ClassVar[str] = "migration_policy"
    schema_version: Literal["grcv4-migration-policy-v1"]
    policy_id: Literal["typed_bidirectional_profile_migration_v1"]
    resource_policy_id: Literal["identity_resource_transport_v1"]
    target_readmission_policy_id: Literal["full_target_fail_closed_v1"]


@dataclass(frozen=True, slots=True, eq=False)
class ResolvedHistoryChannelPolicy(_Record):
    SCHEMA: ClassVar[str] = "history_channel_policy"
    schema_version: Literal["grcv4-history-channel-policy-v1"]
    subject: Literal["candidate", "carrier"]
    policy_id: str
    disposition: Literal[
        "not_applicable", "exact_transport", "target_initializer",
        "whole_carrier_map", "whole_carrier_reset", "explicit_loss", "rederived",
    ]
    source_history_digest: str | None
    target_initializer_id: str | None
    information_loss: Literal["none", "candidate_history_loss", "carrier_history_loss"]


@dataclass(frozen=True, slots=True, eq=False)
class ResolvedHistoryBundlePolicy(_Record):
    SCHEMA: ClassVar[str] = "history_bundle_policy"
    schema_version: Literal["grcv4-history-bundle-policy-v1"]
    candidate: ResolvedHistoryChannelPolicy
    carrier: ResolvedHistoryChannelPolicy

    def __post_init__(self) -> None:
        for name in ("candidate", "carrier"):
            object.__setattr__(self, name, _nested_record(
                getattr(self, name), ResolvedHistoryChannelPolicy))
        _Record.__post_init__(self)


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4MigrationRequest(_Record):
    """Closed declaration, not admitted source/target/history or execution."""

    SCHEMA: ClassVar[str] = "migration_request"
    schema_version: Literal["grcv4-migration-request-v1"]
    operation_id: str
    source_state_digest: str
    target_profile_id: str
    migration_policy: GRCV4MigrationPolicy
    history_policy: ResolvedHistoryBundlePolicy
    target_context_value: FrozenJSONMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "migration_policy", _nested_record(
            self.migration_policy, GRCV4MigrationPolicy))
        object.__setattr__(self, "history_policy", _nested_record(
            self.history_policy, ResolvedHistoryBundlePolicy))
        _Record.__post_init__(self)


def decode_migration_request(
    data: bytes | str, *,
    encoding: Literal["configuration", "canonical"] = "configuration",
) -> GRCV4MigrationRequest:
    """Decode declaration shape only; Tranche 7 owns crossing admission.

    Uses the same explicit configuration/canonical routes as step decoding,
    including numbers nested in target_context_value. A resolved-policy record
    does not establish source history, target support or a lawful crossing.
    """
    return GRCV4MigrationRequest.from_payload(decode_record_payload(
        "migration_request", data, encoding=encoding))
