"""Runtime scope records, provenance witnesses, and execution state.

This provider owns live invocation ledgers, object-flow identity, active-scope
coordination, and the scope-local witnesses derived from those observations.
It depends on candidate and identity providers and uses structural host
contracts instead of importing the concrete binding session or artifacts.
"""

from __future__ import annotations

import hashlib
import pickle
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from types import MappingProxyType, TracebackType
from typing import Any, Final, Literal, Protocol, Self

from .candidates import (
    CandidateDeclaration,
    _candidate_exercise_witness,
    _candidate_target_request_flow,
    _CandidateMechanismEvent,
    _CandidateRequestFloat,
    _CandidateRequestInt,
    _CandidateRequestMapping,
    _CandidateRequestStr,
)
from .identity import (
    CausalPathwayBindingError,
    _callable_bound_owner,
)


class _BindingLock(Protocol):
    @property
    def digest(self) -> str: ...

    def contains_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: Sequence[str],
    ) -> bool: ...

    def contains_crossing_link(
        self,
        *,
        binding_id: str,
        composition_id: str,
        symbol_id: str,
    ) -> bool: ...

    def contains_candidate_mechanism_link(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> bool: ...


class _BoundPathway(Protocol):
    binding_id: str
    pathway_id: str


class _BoundComposition(Protocol):
    binding_id: str
    composition_id: str

    @property
    def contract(self) -> Mapping[str, Any]: ...

    @property
    def source_binding(self) -> _BoundPathway: ...

    @property
    def target_binding(self) -> _BoundPathway: ...


BoundComposition = _BoundComposition


class _RuntimeScopeHost(Protocol):
    @property
    def phase(self) -> str: ...

    @property
    def binding_lock(self) -> _BindingLock | None: ...

    def _scope_composition_is_declared(
        self,
        composition: BoundComposition,
    ) -> bool: ...

    def _scope_candidate_is_declared(
        self,
        candidate: CandidateDeclaration,
    ) -> bool: ...

    def _scope_alternatives_are_declared(
        self,
        alternatives: AllowedPathwayAlternatives,
    ) -> bool: ...


class PathwayBindingSession(Protocol):
    def _runtime_scope_state(self) -> _RuntimeScopeState: ...


ATTESTED_OBJECT_FLOW_DATAFLOW: Final[str] = (
    "externally_attested_runtime_object_flow"
)


EXPLICIT_ADAPTER_DATAFLOW: Final[str] = (
    "exact_explicit_adapter_result_reference"
)


_SPECIAL_COMPOSITION_DATAFLOW_PORTS: Final[
    Mapping[str, tuple[str, str, str, str]]
] = MappingProxyType(
    {
        "CMP-01": (
            "transport_rebuild",
            "argument:state",
            "continuity_and_invariants",
            "receiver_state",
        ),
        "CMP-02": (
            "source_debit",
            "argument:state",
            "target_credit",
            "argument:state",
        ),
        "CMP-03": (
            "transport_rebuild",
            "argument:state",
            "packet_schedule",
            "receiver_base_state",
        ),
        "CMP-04": (
            "diagnostic_model_construction",
            "result_base_state",
            "diagnostic_rebuild",
            "receiver_state",
        ),
        "CMP-17": (
            "assemble_causal_annotation",
            "result",
            "transport_rebuild",
            "argument:evolution",
        ),
        "CMP-21": (
            "target_credit",
            "result",
            "surface_row_emission",
            "argument:processing_result",
        ),
    }
)


def composition_dataflow_contract(
    composition_id: str,
    *,
    explicit_adapter: bool,
) -> dict[str, str]:
    """Return the exact checker-visible flow predicate for one matrix row."""

    if explicit_adapter:
        return {
            "contract_id": f"{composition_id}:explicit-adapter-result:v1",
            "continuity_kind": "exact_adapter_reference",
            "source_stage_id": "*",
            "source_port": "declared_adapter_source_instance",
            "target_stage_id": "*",
            "target_port": "adapter_result_reference",
        }
    ports = _SPECIAL_COMPOSITION_DATAFLOW_PORTS.get(composition_id)
    if ports is None:
        ports = ("*", "receiver", "*", "receiver")
    source_stage_id, source_port, target_stage_id, target_port = ports
    return {
        "contract_id": f"{composition_id}:runtime-object-flow:v1",
        "continuity_kind": (
            "consumer_bound_equivalent_state_copy"
            if composition_id == "CMP-04"
            else "exact_object_identity"
        ),
        "source_stage_id": source_stage_id,
        "source_port": source_port,
        "target_stage_id": target_stage_id,
        "target_port": target_port,
    }


class BindingStateError(CausalPathwayBindingError):
    """Raised when declaration, locking, use, and sealing order is violated."""


@dataclass(frozen=True)
class AllowedPathwayAlternatives:
    """Declared dynamic alternatives; it contains no selection operation."""

    _session: PathwayBindingSession = field(repr=False, compare=False)
    alternative_set_id: str
    pathway_ids: tuple[str, ...]
    selection_authority: str

    def selection_scope(self) -> AlternativeSelectionScope:
        """Return a non-selecting scope that constrains the consumer's choice."""

        return AlternativeSelectionScope(session=self._session, alternatives=self)


@dataclass(frozen=True)
class InvocationRecord:
    """One in-memory I113 use record around real-callable delegation."""

    binding_id: str
    pathway_id: str
    stage_id: str
    symbol_id: str
    composition_ids: tuple[str, ...]
    outcome: str
    return_category: str | None
    effect_contract_id: str | None
    effect_kind: str
    effect_outcome: str
    claim_qualifying_effect: bool
    effect_evidence: Mapping[str, Any] | None
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    runtime_object_flow: Mapping[str, Any]
    candidate_request_flow: Mapping[str, Any] | None
    execution_event_order: int = -1
    crossing_scope_id: str | None = None
    candidate_scope_id: str | None = None
    alternative_selection_scope_id: str | None = None


@dataclass(frozen=True)
class CrossingInvocationRecord:
    """One invocation of a registered composition crossing callable."""

    crossing_scope_id: str
    binding_id: str
    composition_id: str
    symbol_id: str
    source_binding_id: str
    target_binding_id: str
    outcome: str
    return_category: str | None
    effect_contract_id: str | None
    effect_kind: str
    effect_outcome: str
    claim_qualifying_effect: bool
    effect_evidence: Mapping[str, Any] | None
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    execution_event_order: int = -1


@dataclass(frozen=True)
class CandidateMechanismInvocationRecord:
    """One identity-verified invocation of an unregistered candidate callable."""

    candidate_scope_id: str
    candidate_id: str
    mechanism_id: str
    symbol_id: str
    outcome: str
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    relation_review_digest: str | None
    structural_result_observed: bool | None
    runtime_object_flow: Mapping[str, Any]
    execution_event_order: int = -1


_UNRESOLVED_CROSSING_RESULT: Final[object] = object()


class CrossingResultReference:
    """Deferred instance reference to a real crossing callable's result."""

    def __init__(self, *, composition_id: str, target_pathway_id: str) -> None:
        self.composition_id = composition_id
        self.target_pathway_id = target_pathway_id
        self._value: object = _UNRESOLVED_CROSSING_RESULT

    def _set(self, value: object) -> None:
        if self._value is not _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} crossing already returned"
            )
        self._value = value

    def resolve(self) -> object:
        """Return the adapter result or fail before target-stage delegation."""

        if self._value is _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} crossing has not returned"
            )
        return self._value


class FlowDerivedInstanceReference:
    """Deferred target owner bound by the consumer to an exact source result."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
        source_binding_id: str,
        target_binding_id: str,
        target_pathway_id: str,
        source_stage_id: str,
        source_symbol_id: str,
        target_stage_id: str,
        source_port: str,
        target_port: str,
    ) -> None:
        self._runtime = session._runtime_scope_state()
        self.composition_id = composition.composition_id
        self.binding_id = composition.binding_id
        self.source_binding_id = source_binding_id
        self.target_binding_id = target_binding_id
        self.target_pathway_id = target_pathway_id
        self.source_stage_id = source_stage_id
        self.source_symbol_id = source_symbol_id
        self.target_stage_id = target_stage_id
        self.source_port = source_port
        self.target_port = target_port
        self._value: object = _UNRESOLVED_CROSSING_RESULT
        self._derivation: Mapping[str, Any] | None = None

    def bind(
        self,
        *,
        source_result: object,
        target_instance: object,
    ) -> None:
        """Bind one consumer-created target whose carrier is the exact result flow."""

        self._runtime.bind_flow_derived_instance(
            reference=self,
            source_result=source_result,
            target_instance=target_instance,
        )

    def _set(
        self,
        value: object,
        *,
        derivation: Mapping[str, Any],
    ) -> None:
        if self._value is not _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} flow target is already bound"
            )
        self._value = value
        self._derivation = dict(derivation)

    def derivation_record(self) -> Mapping[str, Any]:
        """Return the live-validated derivation attached to the target call."""

        if self._derivation is None:
            raise BindingStateError(
                f"composition {self.composition_id!r} flow target is unresolved"
            )
        return MappingProxyType(dict(self._derivation))

    def resolve(self) -> object:
        """Return the exact consumer-bound target instance."""

        if self._value is _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} flow target is unresolved"
            )
        return self._value


class CompositionExecutionScope:
    """Ordered observed-use scope; it does not dispatch composition mechanics."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
    ) -> None:
        self._runtime = session._runtime_scope_state()
        self.composition = composition
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._runtime.open_composition_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._runtime.close_composition_scope(self)
        return False

    def _record_endpoint(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: InvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "event_kind": "endpoint_stage",
                "record_index": invocation_index,
                "record": record,
            }
        )

    def _record_crossing(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: CrossingInvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "event_kind": "crossing_callable",
                "record_index": invocation_index,
                "record": record,
            }
        )

    def exercise_witness(self) -> dict[str, Any] | None:
        """Return a witness only for complete ordered observed crossing use."""

        if not self._completed:
            return None
        contract = self.composition.contract
        source_binding = self.composition.source_binding
        target_binding = self.composition.target_binding
        source_events: list[dict[str, Any]] = []
        target_events: list[dict[str, Any]] = []
        for stage_id in contract["from_stage_ids"]:
            matches = [
                event
                for event in self._events
                if event["event_kind"] == "endpoint_stage"
                and event["record"].claim_qualifying_effect
                and event["record"].binding_id == source_binding.binding_id
                and event["record"].stage_id == stage_id
            ]
            if not matches:
                return None
            source_events.append(matches[0])
        for stage_id in contract["to_stage_ids"]:
            matches = [
                event
                for event in self._events
                if event["event_kind"] == "endpoint_stage"
                and event["record"].claim_qualifying_effect
                and event["record"].binding_id == target_binding.binding_id
                and event["record"].stage_id == stage_id
            ]
            if not matches:
                return None
            target_events.append(matches[0])
        if max(event["event_order"] for event in source_events) >= min(
            event["event_order"] for event in target_events
        ):
            return None

        crossing_events = [
            event
            for event in self._events
            if event["event_kind"] == "crossing_callable"
            and event["record"].claim_qualifying_effect
            and event["record"].binding_id == self.composition.binding_id
        ]
        adapter_required = (
            contract["composition_status"] == "lawful_with_explicit_adapter"
        )
        dataflow_witness: dict[str, Any] | None
        if adapter_required:
            if len(crossing_events) != 1:
                return None
            crossing_order = crossing_events[0]["event_order"]
            if not (
                max(event["event_order"] for event in source_events)
                < crossing_order
                < min(event["event_order"] for event in target_events)
            ):
                return None
        elif crossing_events:
            return None

        if adapter_required:
            dataflow_requirement = EXPLICIT_ADAPTER_DATAFLOW
            dataflow_witness = {
                "witness_kind": EXPLICIT_ADAPTER_DATAFLOW,
                "crossing_invocation_index": crossing_events[0]["record_index"],
                "source_instance_role": "declared_adapter_source_instance",
                "target_instance_role": "adapter_result_reference",
            }
        else:
            dataflow_requirement = ATTESTED_OBJECT_FLOW_DATAFLOW
            dataflow_witness = self._attested_object_flow_witness(
                source_events,
                target_events,
            )
            if dataflow_witness is None:
                return None

        return {
            "crossing_scope_id": self.scope_id,
            "binding_id": self.composition.binding_id,
            "composition_id": self.composition.composition_id,
            "ordering_rule": "all_from_stages_before_crossing_before_all_to_stages"
            if adapter_required
            else "all_from_stages_before_all_to_stages",
            "from_invocation_indices": [
                event["record_index"] for event in source_events
            ],
            "crossing_invocation_indices": [
                event["record_index"] for event in crossing_events
            ],
            "to_invocation_indices": [event["record_index"] for event in target_events],
            "explicit_adapter_required": adapter_required,
            "explicit_adapter_observed": bool(crossing_events),
            "dataflow_requirement": dataflow_requirement,
            "dataflow_witness": dataflow_witness,
        }

    @staticmethod
    def _flow_port(
        record: InvocationRecord,
        port: str,
    ) -> Mapping[str, str] | None:
        flow = record.runtime_object_flow
        if port.startswith("argument:"):
            arguments = flow.get("arguments", {})
            if not isinstance(arguments, Mapping):
                return None
            value = arguments.get(port.removeprefix("argument:"))
        else:
            value = flow.get(port)
        return value if isinstance(value, Mapping) else None

    def _attested_object_flow_witness(
        self,
        source_events: Sequence[Mapping[str, Any]],
        target_events: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any] | None:
        """Derive the row-specific live object-flow relation."""

        contract = composition_dataflow_contract(
            self.composition.composition_id,
            explicit_adapter=False,
        )
        for source_event in source_events:
            source_record = source_event["record"]
            if contract["source_stage_id"] not in {"*", source_record.stage_id}:
                continue
            source_flow = self._flow_port(source_record, contract["source_port"])
            if source_flow is None:
                continue
            for target_event in target_events:
                target_record = target_event["record"]
                if contract["target_stage_id"] not in {
                    "*",
                    target_record.stage_id,
                }:
                    continue
                target_flow = self._flow_port(
                    target_record,
                    contract["target_port"],
                )
                if target_flow is None:
                    continue
                if source_flow == target_flow:
                    return {
                        "witness_kind": ATTESTED_OBJECT_FLOW_DATAFLOW,
                        "dataflow_contract_id": contract["contract_id"],
                        "continuity_kind": contract["continuity_kind"],
                        "runtime_object_id": source_flow["object_id"],
                        "source_invocation_index": source_event["record_index"],
                        "source_symbol_id": source_record.symbol_id,
                        "source_port": contract["source_port"],
                        "target_invocation_index": target_event["record_index"],
                        "target_symbol_id": target_record.symbol_id,
                        "target_port": contract["target_port"],
                    }
                derivation = target_record.runtime_object_flow.get(
                    "flow_derivation"
                )
                if not (
                    contract["continuity_kind"]
                    == "consumer_bound_equivalent_state_copy"
                    and isinstance(derivation, Mapping)
                    and derivation.get("contract_id") == contract["contract_id"]
                    and derivation.get("source_invocation_index")
                    == source_event["record_index"]
                    and derivation.get("source_port") == contract["source_port"]
                    and derivation.get("target_port") == contract["target_port"]
                    and derivation.get("source_object") == source_flow
                    and derivation.get("target_object") == target_flow
                    and derivation.get("source_value_digest")
                    == derivation.get("target_value_digest")
                ):
                    continue
                assert isinstance(derivation, Mapping)
                return {
                    "witness_kind": ATTESTED_OBJECT_FLOW_DATAFLOW,
                    "dataflow_contract_id": contract["contract_id"],
                    "continuity_kind": contract["continuity_kind"],
                    "source_runtime_object_id": source_flow["object_id"],
                    "target_runtime_object_id": target_flow["object_id"],
                    "state_value_digest": derivation["source_value_digest"],
                    "source_invocation_index": source_event["record_index"],
                    "source_symbol_id": source_record.symbol_id,
                    "source_port": contract["source_port"],
                    "target_invocation_index": target_event["record_index"],
                    "target_symbol_id": target_record.symbol_id,
                    "target_port": contract["target_port"],
                }
        return None


class AlternativeSelectionScope:
    """Consumer-owned choice scope constrained to one declared alternative."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        alternatives: AllowedPathwayAlternatives,
    ) -> None:
        self._runtime = session._runtime_scope_state()
        self.alternatives = alternatives
        self.scope_id = ""
        self._selected_pathway_id: str | None = None
        self._events: list[dict[str, Any]] = []
        self._invalid_pathway_id: str | None = None
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._runtime.open_alternative_selection_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None and self._invalid_pathway_id is None
        self._runtime.close_alternative_selection_scope(self)
        return False

    def _assert_pathway_allowed(self, pathway_id: str) -> None:
        if pathway_id not in self.alternatives.pathway_ids:
            self._invalid_pathway_id = pathway_id
            raise BindingStateError(
                f"pathway {pathway_id!r} is outside alternative set "
                f"{self.alternatives.alternative_set_id!r}"
            )
        if (
            self._selected_pathway_id is not None
            and self._selected_pathway_id != pathway_id
        ):
            self._invalid_pathway_id = pathway_id
            raise BindingStateError(
                f"alternative set {self.alternatives.alternative_set_id!r} "
                f"already selected {self._selected_pathway_id!r}; "
                f"cannot also select {pathway_id!r} in the same scope"
            )
        self._selected_pathway_id = pathway_id

    def _record_invocation(
        self,
        *,
        invocation_index: int,
        record: InvocationRecord,
    ) -> None:
        self._events.append(
            {
                "record_index": invocation_index,
                "record": record,
            }
        )

    def selection_witness(self) -> dict[str, Any] | None:
        """Return one exact choice witness only for a complete scoped call."""

        if (
            not self._completed
            or self._invalid_pathway_id is not None
            or self._selected_pathway_id is None
            or not self._events
        ):
            return None
        if any(
            event["record"].pathway_id != self._selected_pathway_id
            or event["record"].alternative_selection_scope_id != self.scope_id
            for event in self._events
        ):
            return None
        return {
            "selection_scope_id": self.scope_id,
            "alternative_set_id": self.alternatives.alternative_set_id,
            "selection_authority": self.alternatives.selection_authority,
            "selected_pathway_id": self._selected_pathway_id,
            "invocation_indices": [event["record_index"] for event in self._events],
            "returned_invocation_indices": [
                event["record_index"]
                for event in self._events
                if event["record"].outcome == "returned"
            ],
            "claim_qualifying_invocation_indices": [
                event["record_index"]
                for event in self._events
                if event["record"].claim_qualifying_effect
            ],
            "selection_performed_by": "consumer",
        }


class CandidateExecutionScope:
    """Observed constituent-use scope for one unregistered candidate."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        candidate: CandidateDeclaration,
    ) -> None:
        self._runtime = session._runtime_scope_state()
        self.candidate = candidate
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._mechanism_events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._runtime.open_candidate_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._runtime.close_candidate_scope(self)
        return False

    def _record_constituent(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: InvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "record_index": invocation_index,
                "record": record,
            }
        )

    def _record_mechanism(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: CandidateMechanismInvocationRecord,
        result: object | None,
    ) -> None:
        self._mechanism_events.append(
            {
                "event_order": event_order,
                "record_index": invocation_index,
                "record": record,
                "result": result,
            }
        )

    def target_request_flow(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        symbol_id: str,
        positional_arguments: Sequence[Any],
        keyword_arguments: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        """Attest one exact reviewed-candidate mapping expansion."""

        return _candidate_target_request_flow(
            candidate=self.candidate,
            scope_id=self.scope_id,
            mechanism_events=self._mechanism_events,
            mechanism=self.candidate.mechanism(),
            binding_id=binding_id,
            pathway_id=pathway_id,
            symbol_id=symbol_id,
            positional_arguments=positional_arguments,
            keyword_arguments=keyword_arguments,
        )

    def exercise_witness(self) -> dict[str, Any] | None:
        """Return evidence only for completed, returned constituent execution."""

        return _candidate_exercise_witness(
            candidate=self.candidate,
            scope_id=self.scope_id,
            completed=self._completed,
            events=self._events,
            mechanism_events=self._mechanism_events,
        )


class _RuntimeScopeState:
    """Own live object identity, invocation ledgers, and active scope state."""

    def __init__(self, host: _RuntimeScopeHost) -> None:
        self._host = host
        self._direct_runtime_instances: list[object] = []
        self._runtime_flow_objects: list[object] = []
        self._invocations: list[InvocationRecord] = []
        self._invocation_results: dict[int, object] = {}
        self._crossing_invocations: list[CrossingInvocationRecord] = []
        self._candidate_mechanism_invocations: list[
            CandidateMechanismInvocationRecord
        ] = []
        self._composition_scopes: list[CompositionExecutionScope] = []
        self._active_composition_scope: CompositionExecutionScope | None = None
        self._candidate_scopes: list[CandidateExecutionScope] = []
        self._active_candidate_scope: CandidateExecutionScope | None = None
        self._alternative_selection_scopes: list[AlternativeSelectionScope] = []
        self._active_alternative_selection_scope: AlternativeSelectionScope | None = (
            None
        )
        self._execution_event_count = 0

    @property
    def invocations(self) -> tuple[InvocationRecord, ...]:
        return tuple(self._invocations)

    @property
    def crossing_invocations(self) -> tuple[CrossingInvocationRecord, ...]:
        return tuple(self._crossing_invocations)

    @property
    def candidate_mechanism_invocations(
        self,
    ) -> tuple[CandidateMechanismInvocationRecord, ...]:
        return tuple(self._candidate_mechanism_invocations)

    @property
    def composition_scopes(self) -> tuple[CompositionExecutionScope, ...]:
        return tuple(self._composition_scopes)

    @property
    def candidate_scopes(self) -> tuple[CandidateExecutionScope, ...]:
        return tuple(self._candidate_scopes)

    @property
    def alternative_selection_scopes(
        self,
    ) -> tuple[AlternativeSelectionScope, ...]:
        return tuple(self._alternative_selection_scopes)

    def runtime_instance_binding(
        self,
        instance: object | CrossingResultReference | FlowDerivedInstanceReference | None,
        *,
        call_kind: str,
    ) -> dict[str, str] | None:
        """Assign deterministic lock-local identity to one bound call owner."""

        if call_kind != "instance_method" or instance is None:
            return None
        if isinstance(instance, CrossingResultReference):
            return {
                "kind": "adapter_result_reference",
                "instance_id": f"adapter-result:{instance.composition_id}",
            }
        if isinstance(instance, FlowDerivedInstanceReference):
            return {
                "kind": "flow_derived_instance_reference",
                "instance_id": f"flow-result:{instance.composition_id}",
            }
        for index, known in enumerate(self._direct_runtime_instances):
            if known is instance:
                return {
                    "kind": "direct_bound_instance",
                    "instance_id": f"session-instance:{index}",
                }
        index = len(self._direct_runtime_instances)
        self._direct_runtime_instances.append(instance)
        return {
            "kind": "direct_bound_instance",
            "instance_id": f"session-instance:{index}",
        }

    def _runtime_object_descriptor(
        self,
        value: object | None,
    ) -> dict[str, str] | None:
        """Assign one deterministic transcript identity to a live object."""

        if value is None or isinstance(value, (bool, int, float, str, bytes)):
            return None
        for index, known in enumerate(self._runtime_flow_objects):
            if known is value:
                object_id = f"runtime-object:{index}"
                break
        else:
            object_id = f"runtime-object:{len(self._runtime_flow_objects)}"
            self._runtime_flow_objects.append(value)
        value_type = type(value)
        type_module = value_type.__module__
        if value_type in {
            _CandidateRequestInt,
            _CandidateRequestFloat,
            _CandidateRequestStr,
            _CandidateRequestMapping,
        }:
            type_module = "pygrc.causal_pathways.binding"
        return {
            "object_id": object_id,
            "type": f"{type_module}.{value_type.__qualname__}",
        }

    @staticmethod
    def _state_surfaces(
        value: object | None,
    ) -> tuple[object | None, object | None]:
        """Expose only the established GRC/LGRC runtime state carriers."""

        if value is None:
            return None, None
        get_state = getattr(value, "get_state", None)
        if not callable(get_state):
            return None, None
        state = get_state()
        return state, getattr(state, "base_state", None)

    def observe_object_flow(
        self,
        *,
        target: Callable[..., Any],
        arguments: Mapping[str, object],
        result: object | None,
    ) -> dict[str, Any]:
        """Capture receiver, argument, result, and runtime-state object flow."""

        receiver = _callable_bound_owner(target)
        receiver_state, receiver_base_state = self._state_surfaces(receiver)
        result_state, result_base_state = self._state_surfaces(result)
        return {
            "receiver": self._runtime_object_descriptor(receiver),
            "receiver_state": self._runtime_object_descriptor(receiver_state),
            "receiver_base_state": self._runtime_object_descriptor(
                receiver_base_state
            ),
            "arguments": {
                name: self._runtime_object_descriptor(value)
                for name, value in arguments.items()
            },
            "result": self._runtime_object_descriptor(result),
            "result_state": self._runtime_object_descriptor(result_state),
            "result_base_state": self._runtime_object_descriptor(result_base_state),
            "flow_derivation": None,
        }

    @staticmethod
    def attach_flow_derivation(
        runtime_object_flow: dict[str, Any],
        instance_reference: (
            CrossingResultReference | FlowDerivedInstanceReference | None
        ),
    ) -> dict[str, Any]:
        """Attach only a live-validated deferred-instance derivation event."""

        if isinstance(instance_reference, FlowDerivedInstanceReference):
            runtime_object_flow["flow_derivation"] = dict(
                instance_reference.derivation_record()
            )
        return runtime_object_flow

    def authorize_invocation(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: tuple[str, ...],
    ) -> None:
        lock = self._host.binding_lock
        if self._host.phase != "locked" or lock is None:
            raise BindingStateError(
                "claim-bearing bound calls require a frozen pre-execution lock"
            )
        if not lock.contains_link(
            binding_id=binding_id,
            pathway_id=pathway_id,
            stage_id=stage_id,
            symbol_id=symbol_id,
            composition_ids=composition_ids,
        ):
            raise BindingStateError(
                f"symbol {symbol_id!r} is absent from binding lock {lock.digest}"
            )
        if self._active_alternative_selection_scope is not None:
            self._active_alternative_selection_scope._assert_pathway_allowed(pathway_id)

    def candidate_target_request_flow(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        symbol_id: str,
        positional_arguments: Sequence[Any],
        keyword_arguments: Mapping[str, Any],
    ) -> Mapping[str, Any] | None:
        """Return a live-derived reviewed-candidate target request record."""

        scope = self._active_candidate_scope
        if scope is None:
            return None
        return scope.target_request_flow(
            binding_id=binding_id,
            pathway_id=pathway_id,
            symbol_id=symbol_id,
            positional_arguments=positional_arguments,
            keyword_arguments=keyword_arguments,
        )

    def record_invocation(self, record: InvocationRecord) -> None:
        invocation_index = len(self._invocations)
        scope = self._active_composition_scope
        scoped_to_composition = (
            scope is not None
            and scope.composition.composition_id in record.composition_ids
        )
        record = replace(
            record,
            execution_event_order=self._execution_event_count,
            crossing_scope_id=(
                scope.scope_id if scope is not None and scoped_to_composition else None
            ),
            candidate_scope_id=(
                self._active_candidate_scope.scope_id
                if self._active_candidate_scope is not None
                and record.pathway_id
                in self._active_candidate_scope.candidate.consumed_pathway_ids
                else None
            ),
            alternative_selection_scope_id=(
                self._active_alternative_selection_scope.scope_id
                if self._active_alternative_selection_scope is not None
                else None
            ),
        )
        self._invocations.append(record)
        if scope is not None and scoped_to_composition:
            scope._record_endpoint(
                event_order=self._execution_event_count,
                invocation_index=invocation_index,
                record=record,
            )
        candidate_scope = self._active_candidate_scope
        if (
            candidate_scope is not None
            and record.pathway_id in candidate_scope.candidate.consumed_pathway_ids
        ):
            candidate_scope._record_constituent(
                event_order=self._execution_event_count,
                invocation_index=invocation_index,
                record=record,
            )
        if self._active_alternative_selection_scope is not None:
            self._active_alternative_selection_scope._record_invocation(
                invocation_index=invocation_index,
                record=record,
            )
        self._execution_event_count += 1

    def record_invocation_result(
        self,
        *,
        binding_id: str,
        symbol_id: str,
        result: object,
    ) -> None:
        """Retain the live result behind the just-recorded transcript entry."""

        invocation_index = len(self._invocations) - 1
        if invocation_index < 0:
            raise BindingStateError("cannot retain a result without an invocation")
        invocation = self._invocations[invocation_index]
        if (
            invocation.binding_id != binding_id
            or invocation.symbol_id != symbol_id
            or invocation.outcome != "returned"
        ):
            raise BindingStateError("invocation result does not match its transcript")
        self._invocation_results[invocation_index] = result

    @staticmethod
    def _live_flow_port(value: object, port: str) -> object | None:
        """Resolve one approved live-object port without serializing identity."""

        if port in {"result", "receiver"}:
            return value
        state, base_state = _RuntimeScopeState._state_surfaces(value)
        if port in {"result_state", "receiver_state"}:
            return state
        if port in {"result_base_state", "receiver_base_state"}:
            return base_state
        return None

    @staticmethod
    def _live_value_digest(value: object) -> str:
        """Fingerprint one in-process value for an observed copy derivation."""

        try:
            payload = pickle.dumps(value, protocol=5)
        except (pickle.PicklingError, AttributeError, TypeError) as exc:
            raise BindingStateError(
                "flow-derived carrier cannot be deterministically fingerprinted"
            ) from exc
        return hashlib.sha256(payload).hexdigest()

    def bind_flow_derived_instance(
        self,
        *,
        reference: FlowDerivedInstanceReference,
        source_result: object,
        target_instance: object,
    ) -> None:
        """Validate and bind one consumer-created target to exact live object flow."""

        scope = self._active_composition_scope
        if (
            self._host.phase != "locked"
            or self._host.binding_lock is None
            or scope is None
        ):
            raise BindingStateError(
                "flow-derived targets must be bound inside a locked composition scope"
            )
        if (
            scope.composition.binding_id != reference.binding_id
            or scope.composition.composition_id != reference.composition_id
        ):
            raise BindingStateError(
                "flow-derived target does not belong to the active composition scope"
            )
        matching_indices = [
            index
            for index, invocation in enumerate(self._invocations)
            if invocation.binding_id == reference.source_binding_id
            and invocation.stage_id == reference.source_stage_id
            and invocation.symbol_id == reference.source_symbol_id
            and invocation.crossing_scope_id == scope.scope_id
            and invocation.outcome == "returned"
        ]
        if len(matching_indices) != 1:
            raise BindingStateError(
                "flow-derived target requires exactly one returned source invocation"
            )
        retained_result = self._invocation_results.get(matching_indices[0])
        if retained_result is not source_result:
            raise BindingStateError(
                "flow-derived target source_result is not the exact source return"
            )
        source_carrier = self._live_flow_port(source_result, reference.source_port)
        target_carrier = self._live_flow_port(target_instance, reference.target_port)
        if source_carrier is None or target_carrier is None:
            raise BindingStateError(
                "flow-derived target does not preserve the contracted object carrier"
            )
        source_value_digest = self._live_value_digest(source_carrier)
        target_value_digest = self._live_value_digest(target_carrier)
        if source_value_digest != target_value_digest:
            raise BindingStateError(
                "flow-derived target does not preserve the contracted object carrier"
            )
        reference._set(
            target_instance,
            derivation={
                "contract_id": f"{reference.composition_id}:runtime-object-flow:v1",
                "derivation_kind": "consumer_bound_equivalent_state_copy",
                "source_invocation_index": matching_indices[0],
                "source_port": reference.source_port,
                "source_object": self._runtime_object_descriptor(source_carrier),
                "source_value_digest": source_value_digest,
                "target_port": reference.target_port,
                "target_object": self._runtime_object_descriptor(target_carrier),
                "target_value_digest": target_value_digest,
            },
        )

    def record_crossing_invocation(
        self,
        scope: CompositionExecutionScope,
        record: CrossingInvocationRecord,
    ) -> None:
        invocation_index = len(self._crossing_invocations)
        record = replace(record, execution_event_order=self._execution_event_count)
        self._crossing_invocations.append(record)
        scope._record_crossing(
            event_order=self._execution_event_count,
            invocation_index=invocation_index,
            record=record,
        )
        self._execution_event_count += 1

    def record_candidate_mechanism_invocation(
        self,
        scope: CandidateExecutionScope,
        record: CandidateMechanismInvocationRecord,
        *,
        result: object | None,
    ) -> None:
        invocation_index = len(self._candidate_mechanism_invocations)
        record = replace(record, execution_event_order=self._execution_event_count)
        self._candidate_mechanism_invocations.append(record)
        scope._record_mechanism(
            event_order=self._execution_event_count,
            invocation_index=invocation_index,
            record=record,
            result=result,
        )
        self._execution_event_count += 1

    def record_candidate_mechanism_event(
        self,
        scope: Any,
        event: _CandidateMechanismEvent,
        *,
        result: object | None,
    ) -> None:
        """Adapt a candidate-owned event to the runtime invocation ledger."""

        self.record_candidate_mechanism_invocation(
            scope,
            CandidateMechanismInvocationRecord(
                candidate_scope_id=scope.scope_id,
                candidate_id=event.candidate_id,
                mechanism_id=event.mechanism_id,
                symbol_id=event.symbol_id,
                outcome=event.outcome,
                result_type=event.result_type,
                error_type=event.error_type,
                callable_identity=event.callable_identity,
                relation_review_digest=event.relation_review_digest,
                structural_result_observed=event.structural_result_observed,
                runtime_object_flow=event.runtime_object_flow,
            ),
            result=result,
        )

    def open_composition_scope(self, scope: CompositionExecutionScope) -> str:
        if self._host.phase != "locked" or self._host.binding_lock is None:
            raise BindingStateError(
                "composition evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        if not self._host._scope_composition_is_declared(scope.composition):
            raise BindingStateError("composition scope is not declared in this session")
        scope_id = (
            f"{scope.composition.binding_id}:crossing-scope:"
            f"{len(self._composition_scopes)}"
        )
        self._active_composition_scope = scope
        self._composition_scopes.append(scope)
        return scope_id

    def close_composition_scope(self, scope: CompositionExecutionScope) -> None:
        if self._active_composition_scope is not scope:
            raise BindingStateError("composition evidence scope is not active")
        self._active_composition_scope = None

    def open_candidate_scope(self, scope: CandidateExecutionScope) -> str:
        if self._host.phase != "locked" or self._host.binding_lock is None:
            raise BindingStateError(
                "candidate evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        if not self._host._scope_candidate_is_declared(scope.candidate):
            raise BindingStateError("candidate scope is not declared in this session")
        scope_id = (
            f"candidate:{scope.candidate.candidate_id}:evidence-scope:"
            f"{len(self._candidate_scopes)}"
        )
        self._active_candidate_scope = scope
        self._candidate_scopes.append(scope)
        return scope_id

    def close_candidate_scope(self, scope: CandidateExecutionScope) -> None:
        if self._active_candidate_scope is not scope:
            raise BindingStateError("candidate evidence scope is not active")
        self._active_candidate_scope = None

    def open_alternative_selection_scope(
        self,
        scope: AlternativeSelectionScope,
    ) -> str:
        if self._host.phase != "locked" or self._host.binding_lock is None:
            raise BindingStateError(
                "alternative selection scopes require a frozen binding lock"
            )
        if self._active_alternative_selection_scope is not None:
            raise BindingStateError("alternative selection scopes cannot overlap")
        if not self._host._scope_alternatives_are_declared(scope.alternatives):
            raise BindingStateError(
                "alternative selection scope is not declared in this session"
            )
        scope_id = (
            f"alternative:{scope.alternatives.alternative_set_id}:selection-scope:"
            f"{len(self._alternative_selection_scopes)}"
        )
        self._active_alternative_selection_scope = scope
        self._alternative_selection_scopes.append(scope)
        return scope_id

    def close_alternative_selection_scope(
        self,
        scope: AlternativeSelectionScope,
    ) -> None:
        if self._active_alternative_selection_scope is not scope:
            raise BindingStateError("alternative selection scope is not active")
        self._active_alternative_selection_scope = None

    def authorize_crossing(
        self,
        *,
        composition: BoundComposition,
        symbol_id: str,
    ) -> CompositionExecutionScope:
        lock = self._host.binding_lock
        if self._host.phase != "locked" or lock is None:
            raise BindingStateError(
                "composition crossing calls require a frozen binding lock"
            )
        scope = self._active_composition_scope
        if scope is None or scope.composition is not composition:
            raise BindingStateError(
                "composition crossing calls require their explicit evidence scope"
            )
        if not lock.contains_crossing_link(
            binding_id=composition.binding_id,
            composition_id=composition.composition_id,
            symbol_id=symbol_id,
        ):
            raise BindingStateError(
                f"crossing symbol {symbol_id!r} is absent from the binding lock"
            )
        if any(
            item.binding_id == composition.binding_id
            for item in self._crossing_invocations
        ):
            raise BindingStateError(
                f"composition {composition.composition_id!r} crossing was already "
                "invoked"
            )
        return scope

    def authorize_candidate_mechanism(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> CandidateExecutionScope:
        lock = self._host.binding_lock
        if self._host.phase != "locked" or lock is None:
            raise BindingStateError(
                "candidate mechanism calls require a frozen binding lock"
            )
        scope = self._active_candidate_scope
        if scope is None or scope.candidate.candidate_id != candidate_id:
            raise BindingStateError(
                "candidate mechanism calls require their explicit evidence scope"
            )
        if not lock.contains_candidate_mechanism_link(
            candidate_id=candidate_id,
            symbol_id=symbol_id,
        ):
            raise BindingStateError(
                f"candidate mechanism {symbol_id!r} is absent from the binding lock"
            )
        if any(
            item.candidate_id == candidate_id
            for item in self._candidate_mechanism_invocations
        ):
            raise BindingStateError(
                f"candidate {candidate_id!r} mechanism was already invoked"
            )
        return scope

    def candidate_witnesses(
        self,
        candidate: CandidateDeclaration,
    ) -> tuple[dict[str, Any], ...]:
        return tuple(
            witness
            for scope in self._candidate_scopes
            if scope.candidate is candidate
            if (witness := scope.exercise_witness()) is not None
        )

    def composition_witnesses(self) -> tuple[dict[str, Any], ...]:
        witnesses: list[dict[str, Any]] = []
        witnessed_binding_ids: set[str] = set()
        for scope in self._composition_scopes:
            witness = scope.exercise_witness()
            if witness is None:
                continue
            binding_id = str(witness["binding_id"])
            if binding_id in witnessed_binding_ids:
                raise BindingStateError(
                    f"composition binding {binding_id!r} has multiple complete "
                    "execution scopes"
                )
            witnessed_binding_ids.add(binding_id)
            witnesses.append(witness)
        return tuple(witnesses)

    def alternative_selection_witnesses(self) -> tuple[dict[str, Any], ...]:
        witnesses: list[dict[str, Any]] = []
        for scope in self._alternative_selection_scopes:
            witness = scope.selection_witness()
            if witness is None:
                raise BindingStateError(
                    f"alternative selection scope {scope.scope_id!r} is incomplete, "
                    "empty, or contains a rejected choice"
                )
            witnesses.append(witness)
        return tuple(witnesses)

    def assert_no_active_scopes(self) -> None:
        if self._active_composition_scope is not None:
            raise BindingStateError(
                "a receipt cannot be sealed inside a composition evidence scope"
            )
        if self._active_candidate_scope is not None:
            raise BindingStateError(
                "a receipt cannot be sealed inside a candidate evidence scope"
            )
        if self._active_alternative_selection_scope is not None:
            raise BindingStateError(
                "a receipt cannot be sealed inside an alternative selection scope"
            )


__all__ = [
    "ATTESTED_OBJECT_FLOW_DATAFLOW",
    "AllowedPathwayAlternatives",
    "AlternativeSelectionScope",
    "BindingStateError",
    "CandidateExecutionScope",
    "CompositionExecutionScope",
    "CrossingInvocationRecord",
    "CrossingResultReference",
    "FlowDerivedInstanceReference",
    "InvocationRecord",
    "composition_dataflow_contract",
]
