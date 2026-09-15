"""Generic V4 requests and the profile-explicit public lifecycle facade.

Step input shape is weaker than the strict operation request. Migration
records are declarations only: decoding cannot resolve profiles, authenticate
live state or admit a crossing. Mapped-event records likewise declare shape;
lifecycle admission owns graph, affine-map, history and target checks. Harness
hooks, pickle and state restoration are not request inputs.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Literal, Self, TYPE_CHECKING, TypeVar

from ..core.interfaces import GRCModel

from .grc_v4_codec import (
    V4SchemaError,
    canonical_json_bytes,
    decode_canonical_json,
    decode_record_payload,
)
from .grc_v4_profile import GRCV4Profile, GRCV4ResolvedParams, _Record
from .grc_v4_state import (
    FrozenJSONMap, GRCV4State, GRCV4StepResult, GRCV4LifecycleResult,
)

if TYPE_CHECKING:
    from .grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
    from .grc_v4_candidate_a import CandidateADifferentialReference

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


class MissingV4StepRequest(ValueError):
    """The active complete profile has no serialized default step request."""


def decode_step_request_input(
    data: bytes | str,
    *,
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
        "not_applicable",
        "exact_transport",
        "target_initializer",
        "whole_carrier_map",
        "whole_carrier_reset",
        "explicit_loss",
        "rederived",
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
            object.__setattr__(
                self,
                name,
                _nested_record(getattr(self, name), ResolvedHistoryChannelPolicy),
            )
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
        object.__setattr__(
            self,
            "migration_policy",
            _nested_record(self.migration_policy, GRCV4MigrationPolicy),
        )
        object.__setattr__(
            self,
            "history_policy",
            _nested_record(self.history_policy, ResolvedHistoryBundlePolicy),
        )
        _Record.__post_init__(self)


def decode_migration_request(
    data: bytes | str,
    *,
    encoding: Literal["configuration", "canonical"] = "configuration",
) -> GRCV4MigrationRequest:
    """Decode declaration shape only; Tranche 7 owns crossing admission.

    Uses the same explicit configuration/canonical routes as step decoding,
    including numbers nested in target_context_value. A resolved-policy record
    does not establish source history, target support or a lawful crossing.
    """
    return GRCV4MigrationRequest.from_payload(
        decode_record_payload("migration_request", data, encoding=encoding)
    )


@dataclass(frozen=True, slots=True, eq=False)
class ResolvedResourceEventTransform(_Record):
    """Closed affine declaration; dimensions and conservation need live graphs."""

    SCHEMA: ClassVar[str] = "resource_event_transform"
    schema_version: Literal["grcv4-resource-event-transform-v1"]
    policy_id: str
    source_vertex_ids: tuple[str | int, ...]
    target_vertex_ids: tuple[str | int, ...]
    row_major_coefficients: tuple[float, ...]
    target_increment: tuple[float, ...]

    def __post_init__(self) -> None:
        # Validate before normalization: bool, unsafe integer, -0, NaN/Inf and
        # non-sequence containers cannot disappear through tuple/float coercion.
        _Record.__post_init__(self)
        for name in (
            "source_vertex_ids",
            "target_vertex_ids",
            "row_major_coefficients",
            "target_increment",
        ):
            value = getattr(self, name)
            if type(value) not in (tuple, list):
                raise V4SchemaError("affine declaration requires ordered arrays")
            object.__setattr__(self, name, tuple(value))


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4MappedTopologyEventRequest(_Record):
    """Mapped-event request shape only; no live admission or graph mutation."""

    SCHEMA: ClassVar[str] = "mapped_topology_event_request"
    schema_version: Literal["grcv4-mapped-topology-event-request-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    target_graph: FrozenJSONMap
    target_profile_id: str
    resource_transform: ResolvedResourceEventTransform
    history_policy: ResolvedHistoryBundlePolicy
    metadata: FrozenJSONMap

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "resource_transform",
            _nested_record(self.resource_transform, ResolvedResourceEventTransform),
        )
        object.__setattr__(
            self,
            "history_policy",
            _nested_record(self.history_policy, ResolvedHistoryBundlePolicy),
        )
        _Record.__post_init__(self)


@dataclass(frozen=True, slots=True, eq=False)
class GRCV4RepresentationRequest(_Record):
    """Explicit lossless coordinate declaration, distinct from reconstruction."""
    SCHEMA: ClassVar[str] = "representation_request"
    schema_version: Literal["grcv4-representation-transport-request-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    target_graph: FrozenJSONMap
    target_profile_id: str
    correspondence: FrozenJSONMap
    metadata: FrozenJSONMap


def decode_mapped_topology_event_request(
    data: bytes | str,
    *,
    encoding: Literal["configuration", "canonical"] = "configuration",
) -> GRCV4MappedTopologyEventRequest:
    return GRCV4MappedTopologyEventRequest.from_payload(
        decode_record_payload("mapped_topology_event_request", data, encoding=encoding)
    )


class GRCV4(GRCModel):
    """Public generic lifecycle adapter; accepted G2 support stays exact-profile.

    Construction accepts complete, fresh reference-stage inputs. The JSON
    configuration is exactly ``{"initial": inputs.to_payload(), "targets":
    [reference.to_payload(), ...]}``; targets defaults to an empty array and is
    currently restricted to C_OS. Candidate A additionally requires the explicit
    ``differential_reference`` payload bound by its profile. C_OS snapshots keep
    their v3 envelope; other families use the generic v1 envelope. No facade
    cache or request queue exists. Resolved parameters contain any defaults.

    The inherited legacy ABC annotates mutable dataclasses/its own snapshot
    layout, which cannot store V4 authority. Only those inherited return slots
    use Any here; state and step_v4 expose the concrete immutable V4 records.
    This is a structural adapter, not a cast to legacy mutable storage.
    """

    __slots__ = ("_operation",)

    def __init__(
        self,
        initial: GeometryStageInputs,
        *,
        targets: tuple[GRCV4ReferenceGeometry, ...] = (),
        differential_reference: CandidateADifferentialReference | None = None,
        target_differential_references: tuple[CandidateADifferentialReference, ...] = (),
    ) -> None:
        # Lazy import keeps legacy package imports free of V4 numerical extras
        # and avoids a request/lifecycle import cycle.
        from .grc_v4_lifecycle import GRCV4Operation

        self._operation = GRCV4Operation(initial, targets=targets,
                                       differential_reference=differential_reference,
                                       target_differential_references=target_differential_references)

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> Self:
        from .grc_v4_geometry import GeometryStageInputs, GRCV4ReferenceGeometry
        from .grc_v4_candidate_a import CandidateADifferentialReference

        if not isinstance(config, Mapping):
            raise TypeError("V4 configuration must be a mapping")
        if "initial" not in config or set(config) - {"initial", "targets", "differential_reference", "target_differential_references"}:
            raise V4SchemaError("V4 configuration requires initial and optional targets/differential_reference")
        targets = config.get("targets", [])
        if type(targets) is not list:
            raise V4SchemaError("configuration targets must be an ordered array")
        backends = config.get("target_differential_references", [])
        if type(backends) is not list:
            raise V4SchemaError("target differential references must be an ordered array")
        return cls(
            GeometryStageInputs.from_payload(config["initial"]),
            targets=tuple(GRCV4ReferenceGeometry.from_payload(v) for v in targets),
            differential_reference=(None if config.get("differential_reference") is None else
                CandidateADifferentialReference.from_payload(config["differential_reference"])),
            target_differential_references=tuple(CandidateADifferentialReference.from_payload(v) for v in backends),
        )

    @classmethod
    def from_state(cls, state: Mapping[str, Any], params: Mapping[str, Any]) -> Self:
        from .grc_v4_lifecycle import CandidateCOSOperation

        if not isinstance(params, Mapping):
            raise TypeError("from_state requires the serialized resolved parameters")
        operation = CandidateCOSOperation.from_state(state, params)
        result = cls.__new__(cls)
        result._operation = operation
        return result

    @property
    def state(self) -> GRCV4State:
        return GRCV4State(self._operation.state)

    def get_state(self) -> Any:
        """Return the immutable GRCV4State common-surface projection."""
        return self.state

    def set_state(self, state: object) -> None:
        if type(state) is not GRCV4State:
            raise TypeError("expected a GRCV4State projection")
        self._operation.set_state(state.lifecycle)

    def get_params(self) -> GRCV4ResolvedParams:
        return self._operation.reference.profile.params_resolved

    def snapshot(self) -> Any:
        return self._operation.snapshot()

    def save(self, path: str) -> None:
        self._operation.save(path)

    @classmethod
    def load(cls, path: str) -> Self:
        from .grc_v4_lifecycle import CandidateCOSOperation

        operation = CandidateCOSOperation.load(path)
        result = cls.__new__(cls)
        result._operation = operation
        return result

    def duplicate(self) -> Self:
        # Capture parameters with the same atomic snapshot, never a second read.
        snapshot = self.snapshot()
        return type(self).from_state(
            snapshot, snapshot["reference"]["profile"]["params_resolved"]
        )

    def __copy__(self) -> Self:
        return self.duplicate()

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        result = self.duplicate()
        memo[id(self)] = result
        return result

    def reset(self) -> None:
        self._operation.reset()

    def rebase_reset_baseline(self) -> None:
        self._operation.rebase_reset_baseline()

    def step_v4(self, request: GRCV4StepRequest) -> GRCV4StepResult:
        if type(request) is not GRCV4StepRequest:
            raise TypeError("step_v4 requires a strict GRCV4StepRequest")
        request = GRCV4StepRequest.from_payload(request.to_payload())
        payload = request.to_payload()
        payload["schema_version"] = "grcv4-step-request-input-v1"
        return self.step_v4_input(GRCV4StepRequestInput.from_payload(payload))

    def step_v4_input(self, request: GRCV4StepRequestInput) -> GRCV4StepResult:
        """External admission, including typed negative-duration rejection.

        Use decode_step_request_input for wire input. Shape errors raise before
        admission; semantic failures return noncommitting failure results.
        """
        return self._operation.step_v4(request)

    def run_v4(self, requests: Iterable[GRCV4StepRequest]) -> list[GRCV4StepResult]:
        # Do not preconsume the iterator or erase earlier commits if it raises.
        return [self.step_v4(request) for request in requests]

    def step(self) -> Any:
        """Use only the active profile's immutable serialized default."""
        return self._operation.step_default()

    def run(self, num_steps: int) -> list[Any]:
        if type(num_steps) is not int:
            raise TypeError("num_steps must be an integer, not bool")
        if num_steps < 0:
            raise ValueError("num_steps must be nonnegative")
        return [self.step() for _ in range(num_steps)]

    def migrate_profile(self, request: GRCV4MigrationRequest) -> GRCV4LifecycleResult:
        return self._operation.migrate_profile(request)

    def apply_topology_event(
        self, request: GRCV4MappedTopologyEventRequest
    ) -> GRCV4LifecycleResult:
        return self._operation.apply_topology_event(request)

    def compute_observables(self) -> dict[str, Any]:
        return self._operation.compute_observables()

    def reconstruct_topology_event(self, request: GRCV4MappedTopologyEventRequest) -> GRCV4LifecycleResult:
        return self._operation.reconstruct_topology_event(request)

    def transport_representation(self, request: GRCV4RepresentationRequest) -> GRCV4LifecycleResult:
        return self._operation.transport_representation(request)

    @property
    def active_profile_id(self) -> str:
        return self._operation.reference.profile.complete_profile_id

    @property
    def active_model_identity(self) -> str:
        return self.active_profile_id

    def list_supported_profiles(self) -> frozenset[str]:
        """Exact local construction/crossing targets, not accepted conformance."""
        return self._operation.list_supported_profiles()

    def get_supported_profile(self, complete_profile_id: str) -> GRCV4Profile:
        return self._operation.get_supported_profile(complete_profile_id)

    def list_supported_model_identities(self) -> frozenset[str]:
        return self.list_supported_profiles()

    def list_capabilities(self) -> set[str]:
        """Executable active-profile methods, not a G2/GRC9 advertisement."""
        identity = self._operation.reference.profile.identity_payload
        capabilities = {
            "profile_explicit_v4", "single_resource_ledger",
            "authoritative_current", "structural_hodge_geometry",
            "quadrature_budget",
            "v4_explicit_history_reconstruction", "v4_pure_representation_transport",
            "v4_candidate_c_derived_sector" if identity.candidate == "C" else "v4_candidate_a_retained_history",
            "v4_realization_" + identity.realization.lower().replace("+", "_"),
        }
        if identity.profile_family_id == "C_OS":
            capabilities.update({"typed_topology_events", "profile_migration"})
        elif len(self.list_supported_profiles()) > 1:
            capabilities.add("profile_migration")
        return capabilities
