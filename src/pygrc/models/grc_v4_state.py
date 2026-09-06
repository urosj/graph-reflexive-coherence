"""V4-owned immutable value records, not profile or lifecycle admission.

P9-2.1 implements the ownership boundary in the V4 state/interface specs.
Constructors detach all mutable input before checking local shape. Identity
strings are supplied, never generated or authenticated here. Profile/receipt
payloads require the later codec, admission and lifecycle layers before use by
an executable model. There are no caches, runtime capabilities or model exports.
"""

from __future__ import annotations

from collections import UserString
from collections.abc import ItemsView, Iterator, Mapping, Sequence, Set
from dataclasses import dataclass, field
import math
from numbers import Integral, Real
from typing import Any, Literal, Protocol, TypeAlias, runtime_checkable

from pygrc.core.events import GRCEvent

FrozenJSONValue: TypeAlias = (
    "None | bool | int | float | str | tuple[FrozenJSONValue, ...] | FrozenJSONMap"
)
ImmutableFloatArray: TypeAlias = tuple[float, ...]
OperationDisposition: TypeAlias = Literal["committed", "rejected"]
SolverDisposition: TypeAlias = Literal[
    "valid_root",
    "domain_failure",
    "singular",
    "conditioning_failure",
    "nonfinite",
    "no_admitted_root",
    "multiple_admitted_roots",
]


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("expected a real number, not a boolean or coercible object")
    if isinstance(value, Integral):
        # Convert exactly BEFORE abs/range/float: fixed-width abs can overflow,
        # and float conversion can erase the out-of-range source integer.
        value = int(value)
        if abs(value) > 2**53 - 1:
            raise ValueError("integer outside the I-JSON safe range")
    result = float(value)
    if not math.isfinite(result) or (result == 0 and math.copysign(1, result) < 0):
        raise ValueError("nonfinite numbers and negative zero are forbidden")
    return result


def _index(value: object) -> None:
    if type(value) is not int or not 0 <= value <= 2**53 - 1:
        raise ValueError("step_index must be a nonnegative safe integer")


def _text(value: object) -> None:
    if type(value) is not str or not value:
        raise ValueError("expected a nonempty identity or label")
    value.encode("utf-8")  # Reject lone surrogates, without Unicode normalization.


def _freeze(value: object, active: set[int]) -> FrozenJSONValue:
    if value is None or type(value) is bool:
        return value
    if type(value) is str:
        value.encode("utf-8")
        return value
    if type(value) is int or type(value) is float:
        _number(value)
        return value
    if not isinstance(value, Mapping) and type(value) not in (tuple, list):
        raise TypeError("expected JSON values; arbitrary objects are not frozen")
    if id(value) in active:
        raise ValueError("cyclic payload is not a JSON value")
    active.add(id(value))
    try:
        if isinstance(value, Mapping):
            pairs: list[tuple[str, FrozenJSONValue]] = []
            seen: set[str] = set()
            for key, item in value.items():
                if type(key) is not str:
                    raise TypeError("JSON object keys must be strings")
                key.encode("utf-8")
                if key in seen:
                    raise ValueError("duplicate mapping key")
                seen.add(key)
                pairs.append((key, _freeze(item, active)))
            result = object.__new__(FrozenJSONMap)
            object.__setattr__(result, "_items", tuple(pairs))
            return result
        if isinstance(value, (list, tuple)):
            return tuple(_freeze(item, active) for item in value)
        raise TypeError("expected a JSON sequence")
    finally:
        active.remove(id(value))


@dataclass(frozen=True, slots=True, init=False, eq=False)
class FrozenJSONMap(Mapping[str, FrozenJSONValue]):
    """Detached JSON mapping with no writable backing dictionary or array.

    Python mapping equality/hash are NOT JSON identity: bool and number values
    may compare equal. Admission/codec consumers must use typed/JCS identity,
    not this equality, hash(), dataclasses.asdict(), or dataclasses.replace().
    Explicit reinitialization/pickle hooks are not supported mutation APIs.
    """

    _items: tuple[tuple[str, FrozenJSONValue], ...]

    def __init__(self, value: Mapping[str, object]) -> None:
        frozen = _freeze(value, set())
        if not isinstance(frozen, FrozenJSONMap):
            raise TypeError("expected a mapping")
        object.__setattr__(self, "_items", frozen._items)

    def __getitem__(self, key: str) -> FrozenJSONValue:
        for name, value in self._items:
            if name == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def items(self) -> ItemsView[str, FrozenJSONValue]:
        # Mapping's default view performs one linear lookup per item. This
        # immutable view walks the existing tuple directly, including during
        # recursive freezing, equality and codec projection.
        return _FrozenItemsView(self)

    def __hash__(self) -> int:
        return hash(frozenset(self._items))

    def to_dict(self) -> dict[str, object]:
        """Return detached JSON data, not canonical bytes or an admitted snapshot."""
        return {key: _thaw(value) for key, value in self._items}


class _FrozenItemsView(ItemsView[str, FrozenJSONValue]):
    _mapping: Mapping[str, FrozenJSONValue]

    def __iter__(self) -> Iterator[tuple[str, FrozenJSONValue]]:
        mapping = self._mapping
        assert isinstance(mapping, FrozenJSONMap)
        return iter(mapping._items)


def _thaw(value: FrozenJSONValue) -> object:
    if isinstance(value, FrozenJSONMap):
        return value.to_dict()
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _vector(
    value: Any, *, positive: bool = False, nonnegative: bool = False
) -> ImmutableFloatArray:
    """Copy an ordered sequence or one-dimensional native numeric buffer.

    Any is confined to this dynamic input-adapter boundary; stored values are
    plain float tuples. Raw byte/text/mapping/set inputs and one-shot iterators
    have no coordinate interpretation here. Explicit numeric memoryviews are
    supported, including strided/reversed views, without flattening or casting.
    """
    if isinstance(value, (Mapping, Set, str, UserString, bytes, bytearray, Iterator)):
        raise TypeError("coordinates require an ordered numeric sequence or view")
    try:
        view = memoryview(value)
    except TypeError:
        if not isinstance(value, Sequence):
            raise TypeError("untyped iterable is not a coordinate sequence") from None
        values = value
    else:
        # Restrict to native scalar formats that memoryview can iterate exactly.
        # In particular, object, bool, structured, and multidimensional arrays
        # cannot become coordinate vectors by implicit coercion or flattening.
        if view.ndim != 1 or view.format not in {
            "b",
            "B",
            "h",
            "H",
            "i",
            "I",
            "l",
            "L",
            "q",
            "Q",
            "f",
            "d",
        }:
            raise TypeError("coordinates require a one-dimensional native numeric view")
        values = view
    result = tuple(_number(item) for item in values)
    if positive and any(item <= 0 for item in result):
        raise ValueError("W_A must be strictly positive")
    if nonnegative and any(item < 0 for item in result):
        raise ValueError("C must be nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class GRCV4AuthoritativeState:
    C: ImmutableFloatArray
    W_A: ImmutableFloatArray | None
    Z_4: ImmutableFloatArray | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "C", _vector(self.C, nonnegative=True))
        if self.W_A is not None:
            object.__setattr__(self, "W_A", _vector(self.W_A, positive=True))
        if self.Z_4 is not None:
            object.__setattr__(self, "Z_4", _vector(self.Z_4))


def _authority(value: GRCV4AuthoritativeState) -> GRCV4AuthoritativeState:
    if type(value) is not GRCV4AuthoritativeState:
        raise TypeError("expected a V4 authoritative record")
    return GRCV4AuthoritativeState(value.C, value.W_A, value.Z_4)


@dataclass(frozen=True, slots=True)
class GRCV4ResetBaseline:
    authoritative: GRCV4AuthoritativeState
    graph_digest: str
    orientation_identity: str
    active_model_identity: str
    context_contract_id: str
    Q_target: float
    reset_digest: str
    schema_version: Literal["grcv4-reset-baseline-v1"] = field(
        default="grcv4-reset-baseline-v1", init=False
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "authoritative", _authority(self.authoritative))
        object.__setattr__(self, "Q_target", _number(self.Q_target))
        for value in (
            self.graph_digest,
            self.orientation_identity,
            self.active_model_identity,
            self.context_contract_id,
            self.reset_digest,
        ):
            _text(value)


@dataclass(frozen=True, slots=True)
class GRCV4LifecycleState:
    step_index: int
    time: float
    graph: FrozenJSONMap
    graph_digest: str
    orientation_identity: str
    profile: FrozenJSONMap
    context_contract_id: str
    context_value_digest: str | None
    current: GRCV4AuthoritativeState
    reset: GRCV4ResetBaseline
    Q_target: float
    receipt_ledger: tuple[FrozenJSONMap, ...]
    scientific_state_digest: str
    lifecycle_digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "graph", FrozenJSONMap(self.graph))
        object.__setattr__(self, "profile", FrozenJSONMap(self.profile))
        object.__setattr__(self, "current", _authority(self.current))
        if type(self.reset) is not GRCV4ResetBaseline:
            raise TypeError("expected a reduced V4 reset baseline")
        object.__setattr__(
            self,
            "receipt_ledger",
            tuple(FrozenJSONMap(item) for item in self.receipt_ledger),
        )
        object.__setattr__(self, "time", _number(self.time))
        object.__setattr__(self, "Q_target", _number(self.Q_target))
        _index(self.step_index)
        if self.time < 0:
            raise ValueError("time must be nonnegative")
        for value in (
            self.graph_digest,
            self.orientation_identity,
            self.context_contract_id,
            self.scientific_state_digest,
            self.lifecycle_digest,
        ):
            _text(value)
        if self.context_value_digest is not None:
            _text(self.context_value_digest)
        if set(self.profile) != {
            "identity_payload",
            "params_resolved",
            "complete_profile_id",
        }:
            raise ValueError("profile must retain its payload, parameters and identity")
        identity = self.profile["identity_payload"]
        if not isinstance(identity, FrozenJSONMap) or not isinstance(
            self.profile["params_resolved"], FrozenJSONMap
        ):
            raise TypeError("profile payload and parameters must be mappings")
        _text(self.profile["complete_profile_id"])
        candidate, realization = identity["candidate"], identity["realization"]
        if candidate not in ("A", "C") or realization not in (
            "CI",
            "OS",
            "RG2b",
            "PC",
            "CI+PC",
        ):
            raise ValueError("unknown authority-coordinate shape")
        for state in (self.current, self.reset.authoritative):
            if (state.W_A is not None) != (candidate == "A"):
                raise ValueError("candidate/history authority mismatch")
            if (state.Z_4 is not None) != (realization in ("PC", "CI+PC")):
                raise ValueError("realization/carrier authority mismatch")
        if any(
            (
                self.reset.graph_digest != self.graph_digest,
                self.reset.orientation_identity != self.orientation_identity,
                self.reset.context_contract_id != self.context_contract_id,
                self.reset.Q_target != self.Q_target,
            )
        ):
            raise ValueError("current/reset lifecycle context mismatch")
        # Full graph/profile/domain/charge/digest validation is not performed here.


@runtime_checkable
class GRCStateSurface(Protocol):
    @property
    def step_index(self) -> int: ...
    @property
    def time(self) -> float: ...
    @property
    def budget_target(self) -> float: ...
    @property
    def remainder(self) -> float | None: ...


@dataclass(frozen=True, slots=True)
class GRCV4State:
    lifecycle: GRCV4LifecycleState

    def __post_init__(self) -> None:
        if type(self.lifecycle) is not GRCV4LifecycleState:
            raise TypeError("expected a V4 lifecycle record")

    @property
    def step_index(self) -> int:
        return self.lifecycle.step_index

    @property
    def time(self) -> float:
        return self.lifecycle.time

    @property
    def budget_target(self) -> float:
        return self.lifecycle.Q_target

    @property
    def remainder(self) -> None:
        return None


@dataclass(frozen=True, slots=True)
class GRCV4Event:
    """Immutable structural counterpart of the unchanged common GRCEvent."""

    kind: str
    step_index: int
    payload: FrozenJSONMap
    source_family: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", FrozenJSONMap(self.payload))
        _text(self.kind)
        _index(self.step_index)
        if self.source_family is not None:
            _text(self.source_family)

    def to_common_event(self) -> GRCEvent:
        """A mutable legacy-shaped copy; edits cannot reach this value."""
        return GRCEvent(
            self.kind, self.step_index, self.payload.to_dict(), self.source_family
        )


@runtime_checkable
class StepResultSurface(Protocol):
    @property
    def step_index(self) -> int: ...
    @property
    def time(self) -> float: ...
    @property
    def events(self) -> Sequence[GRCEvent]: ...
    @property
    def observables(self) -> Mapping[str, FrozenJSONValue]: ...


@dataclass(frozen=True, slots=True, init=False)
class GRCV4StepResult:
    step_index: int
    time: float
    _events: tuple[GRCV4Event, ...] = field(repr=False)
    observables: FrozenJSONMap
    active_profile_id: str
    active_model_identity: str
    operation_disposition: OperationDisposition
    solver_disposition: SolverDisposition | None
    committed: bool
    commit_id: str | None
    failure: FrozenJSONMap | None
    emitted_receipts: tuple[FrozenJSONMap, ...]
    schema_version: Literal["grcv4-step-result-v1"] = field(
        default="grcv4-step-result-v1", init=False
    )

    def __init__(
        self,
        step_index: int,
        time: float,
        events: Sequence[GRCV4Event | GRCEvent],
        observables: Mapping[str, object],
        active_profile_id: str,
        active_model_identity: str,
        operation_disposition: OperationDisposition,
        solver_disposition: SolverDisposition | None,
        committed: bool,
        commit_id: str | None,
        failure: Mapping[str, object] | None,
        emitted_receipts: Sequence[Mapping[str, object]],
    ) -> None:
        frozen_events = []
        for event in events:
            if type(event) not in (GRCV4Event, GRCEvent):
                raise TypeError("expected a common or V4 event")
            frozen_events.append(
                GRCV4Event(
                    event.kind,
                    event.step_index,
                    FrozenJSONMap(event.payload),
                    event.source_family,
                )
            )
        object.__setattr__(self, "_events", tuple(frozen_events))
        object.__setattr__(self, "observables", FrozenJSONMap(observables))
        object.__setattr__(
            self,
            "emitted_receipts",
            tuple(FrozenJSONMap(item) for item in emitted_receipts),
        )
        object.__setattr__(
            self, "failure", None if failure is None else FrozenJSONMap(failure)
        )
        object.__setattr__(self, "time", _number(time))
        object.__setattr__(self, "step_index", step_index)
        object.__setattr__(self, "active_profile_id", active_profile_id)
        object.__setattr__(self, "active_model_identity", active_model_identity)
        object.__setattr__(self, "operation_disposition", operation_disposition)
        object.__setattr__(self, "solver_disposition", solver_disposition)
        object.__setattr__(self, "committed", committed)
        object.__setattr__(self, "commit_id", commit_id)
        object.__setattr__(self, "schema_version", "grcv4-step-result-v1")
        _index(self.step_index)
        if self.time < 0:
            raise ValueError("time must be nonnegative")
        _text(self.active_profile_id)
        _text(self.active_model_identity)
        _text(self.operation_disposition)
        if self.solver_disposition is not None:
            _text(self.solver_disposition)
        if type(self.committed) is not bool:
            raise TypeError("committed must be boolean")
        if self.operation_disposition not in ("committed", "rejected"):
            raise ValueError("invalid operation disposition")
        if self.solver_disposition not in (
            None,
            "valid_root",
            "domain_failure",
            "singular",
            "conditioning_failure",
            "nonfinite",
            "no_admitted_root",
            "multiple_admitted_roots",
        ):
            raise ValueError("invalid solver disposition")
        if self.committed:
            if (
                self.operation_disposition != "committed"
                or self.failure is not None
                or self.solver_disposition != "valid_root"
            ):
                raise ValueError("inconsistent committed step result")
            _text(self.commit_id)
        elif (
            self.operation_disposition != "rejected"
            or self.failure is None
            or self.commit_id is not None
        ):
            raise ValueError("inconsistent rejected step result")

    @property
    def events(self) -> tuple[GRCEvent, ...]:
        """Common nominal event type, freshly copied on every read."""
        return tuple(event.to_common_event() for event in self._events)


@dataclass(frozen=True, slots=True)
class GRCV4LifecycleResult:
    operation_disposition: OperationDisposition
    committed: bool
    commit_id: str | None
    failure: FrozenJSONMap | None
    emitted_receipts: tuple[FrozenJSONMap, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "emitted_receipts",
            tuple(FrozenJSONMap(item) for item in self.emitted_receipts),
        )
        if self.failure is not None:
            object.__setattr__(self, "failure", FrozenJSONMap(self.failure))
        _text(self.operation_disposition)
        if type(self.committed) is not bool:
            raise TypeError("committed must be boolean")
        if self.committed:
            if self.operation_disposition != "committed" or self.failure is not None:
                raise ValueError("inconsistent committed lifecycle result")
            _text(self.commit_id)
        elif (
            self.operation_disposition != "rejected"
            or self.failure is None
            or self.commit_id is not None
        ):
            raise ValueError("inconsistent rejected lifecycle result")
