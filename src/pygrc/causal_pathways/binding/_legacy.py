"""Private compatibility implementation for causal-pathway binding.

This module is retained temporarily while cohesive responsibilities move into
the ``pygrc.causal_pathways.binding`` package. It is not a public import path.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import pickle
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType, TracebackType
from typing import Any, Final, Literal, Self

from .authority import CausalPathwayAuthority, UnknownPathwayError
from .candidates import (
    INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT,
    CandidateDeclaration,
    CandidateUseRecord,
    InvalidCandidateError,
    VerifiedCandidateMechanism,
    _build_candidate_declaration,
    _candidate_exercise_witness,
    _candidate_target_request_flow,
    _CandidateMechanismEvent,
    _CandidateRequestFloat,
    _CandidateRequestInt,
    _CandidateRequestMapping,
    _CandidateRequestStr,
)
from .effects import EFFECT_OUTCOMES, _classify_returned_effect
from .identity import (
    CausalPathwayBindingError,
    CompositionCrossingBinding,
    SourceSymbolBinding,
    SymbolBindingError,
    _callable_bound_owner,
    _callable_definition,
    _CallableIdentityGuard,
    _canonical_value_digest,
    _VerifiedSourceFile,
    canonical_digest,
)

EXECUTABLE_COMPOSITION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "lawful_native",
        "lawful_with_explicit_adapter",
        "diagnostic_only",
        "producer_mediated",
    }
)

CLAIM_SCOPE_BOUND_INVOCATIONS: Final[str] = "bound_invocations_only"
UNTRACKED_EXECUTION_STATUS: Final[str] = "not_observable_by_binding_plane"
EXPLICIT_ADAPTER_DATAFLOW: Final[str] = (
    "exact_explicit_adapter_result_reference"
)
ATTESTED_OBJECT_FLOW_DATAFLOW: Final[str] = (
    "externally_attested_runtime_object_flow"
)
EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT: Final[str] = (
    "externally_supplied_digest_for_registered_composition_or_reviewed_candidate"
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



class UnbindableCompositionError(CausalPathwayBindingError):
    """Raised when a registered row is missing or an invalid relabel."""


class BindingStateError(CausalPathwayBindingError):
    """Raised when declaration, locking, use, and sealing order is violated."""


def execution_transcript_digest(
    *,
    binding_lock_digest: str,
    stage_invocations: Sequence[Mapping[str, Any]],
    crossing_invocations: Sequence[Mapping[str, Any]],
    candidate_mechanism_invocations: Sequence[Mapping[str, Any]],
) -> str:
    """Digest only raw live-execution records, not their derived claims."""

    return _canonical_value_digest(
        {
            "schema_version": "causal_pathway_execution_transcript_v1",
            "binding_lock_digest": binding_lock_digest,
            "stage_invocations": list(stage_invocations),
            "crossing_invocations": list(crossing_invocations),
            "candidate_mechanism_invocations": list(
                candidate_mechanism_invocations
            ),
        }
    )


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
        self._session = session
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

        self._session._bind_flow_derived_instance(
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


class VerifiedCallable:
    """Callable link that preserves the linked mechanism's arguments and result."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        composition_ids: tuple[str, ...],
        symbol: SourceSymbolBinding,
        instance: object | CrossingResultReference | FlowDerivedInstanceReference | None,
    ) -> None:
        target = symbol.resolve()
        instance_reference = (
            instance
            if isinstance(
                instance,
                (CrossingResultReference, FlowDerivedInstanceReference),
            )
            else None
        )
        if instance_reference is not None:
            if symbol.call_kind != "instance_method":
                raise SymbolBindingError(
                    f"{symbol.symbol_id!r} cannot use a deferred instance"
                )
        elif instance is not None:
            if symbol.call_kind != "instance_method":
                raise SymbolBindingError(
                    f"{symbol.symbol_id!r} is not an instance method"
                )
            target = target.__get__(instance, type(instance))
        identity_guard = session._callable_identity_guard(symbol, target)
        self._session = session
        self._binding_id = binding_id
        self._pathway_id = pathway_id
        self._stage_id = stage_id
        self._composition_ids = composition_ids
        self._symbol = symbol
        self._target = target
        self._instance_reference = instance_reference
        self._expected_definition = _callable_definition(target)
        self._expected_bound_owner = _callable_bound_owner(target)
        self._identity_guard = identity_guard
        self.__name__ = getattr(target, "__name__", symbol.qualified_symbol)
        self.__doc__ = getattr(target, "__doc__", None)
        signature = inspect.signature(target)
        if instance_reference is not None:
            parameters = tuple(signature.parameters.values())
            if parameters and parameters[0].name in {"self", "cls"}:
                signature = signature.replace(parameters=parameters[1:])
        self.__signature__ = signature

    @property
    def symbol_id(self) -> str:
        return self._symbol.symbol_id

    @property
    def linked_callable(self) -> Callable[..., Any]:
        if self._instance_reference is None:
            return self._target
        target, _ = self._assert_current_callable()
        return target

    @property
    def callable_identity(self) -> Mapping[str, Any]:
        """Return the callable identity frozen for this handle."""

        return self._identity_guard.identity_record

    def _assert_current_callable(
        self,
    ) -> tuple[Callable[..., Any], Mapping[str, Any]]:
        """Fail before delegation if the resolved or stored target has changed."""

        current = self._symbol.resolve()
        if self._symbol.call_kind == "instance_method":
            if self._instance_reference is not None:
                owner = self._instance_reference.resolve()
            else:
                owner = self._expected_bound_owner
            if owner is None:
                raise SymbolBindingError(
                    f"binding {self._symbol.symbol_id!r} lost its instance owner"
                )
            current = current.__get__(owner, type(owner))
        identity_changed = (
            _callable_definition(current) is not self._expected_definition
            or _callable_definition(self._target) is not self._expected_definition
        )
        if self._instance_reference is None:
            identity_changed = identity_changed or (
                _callable_bound_owner(current) is not self._expected_bound_owner
                or _callable_bound_owner(self._target) is not self._expected_bound_owner
            )
        if identity_changed:
            raise SymbolBindingError(
                f"binding {self._symbol.symbol_id!r} callable identity changed"
            )
        current_identity = self._identity_guard.assert_current(current)
        return current, current_identity

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._session._assert_invocation_allowed(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            stage_id=self._stage_id,
            symbol_id=self._symbol.symbol_id,
            composition_ids=self._composition_ids,
        )
        target, callable_identity = self._assert_current_callable()
        candidate_request_flow = self._session._candidate_target_request_flow(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            symbol_id=self._symbol.symbol_id,
            positional_arguments=args,
            keyword_arguments=kwargs,
        )
        effect_contract = self._session.authority.effect_outcome_contract(
            self._symbol.symbol_id
        )
        for name, expected in self._symbol.required_keyword_arguments.items():
            if kwargs.get(name) != expected:
                raise SymbolBindingError(
                    f"binding {self._symbol.symbol_id!r} requires {name}={expected!r}"
                )
        pre_call_effect_evidence = (
            effect_contract.capture_pre_call_evidence(target)
            if effect_contract is not None
            else None
        )
        try:
            bound_arguments = dict(
                inspect.signature(target).bind(*args, **kwargs).arguments
            )
        except TypeError:
            bound_arguments = {}
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            runtime_object_flow = self._session._runtime_object_flow(
                target=target,
                arguments=bound_arguments,
                result=None,
            )
            runtime_object_flow = self._session._attach_flow_derivation(
                runtime_object_flow,
                self._instance_reference,
            )
            self._session._record_invocation(
                InvocationRecord(
                    binding_id=self._binding_id,
                    pathway_id=self._pathway_id,
                    stage_id=self._stage_id,
                    symbol_id=self._symbol.symbol_id,
                    composition_ids=self._composition_ids,
                    outcome="raised",
                    return_category=None,
                    effect_contract_id=(
                        effect_contract.contract_id
                        if effect_contract is not None
                        else None
                    ),
                    effect_kind=(
                        effect_contract.effect_kind
                        if effect_contract is not None
                        else "unreviewed"
                    ),
                    effect_outcome="unknown",
                    claim_qualifying_effect=False,
                    effect_evidence=None,
                    result_type=None,
                    error_type=type(exc).__name__,
                    callable_identity=callable_identity,
                    runtime_object_flow=runtime_object_flow,
                    candidate_request_flow=candidate_request_flow,
                )
            )
            raise
        runtime_object_flow = self._session._runtime_object_flow(
            target=target,
            arguments=bound_arguments,
            result=result,
        )
        runtime_object_flow = self._session._attach_flow_derivation(
            runtime_object_flow,
            self._instance_reference,
        )
        (
            return_category,
            effect_contract_id,
            effect_kind,
            effect_outcome,
            claim_qualifying_effect,
            effect_evidence,
        ) = _classify_returned_effect(
            self._session.authority,
            self._symbol.symbol_id,
            result,
            target=target,
            pre_call_evidence=pre_call_effect_evidence,
        )
        self._session._record_invocation(
            InvocationRecord(
                binding_id=self._binding_id,
                pathway_id=self._pathway_id,
                stage_id=self._stage_id,
                symbol_id=self._symbol.symbol_id,
                composition_ids=self._composition_ids,
                outcome="returned",
                return_category=return_category,
                effect_contract_id=effect_contract_id,
                effect_kind=effect_kind,
                effect_outcome=effect_outcome,
                claim_qualifying_effect=claim_qualifying_effect,
                effect_evidence=effect_evidence,
                result_type=type(result).__name__,
                error_type=None,
                callable_identity=callable_identity,
                runtime_object_flow=runtime_object_flow,
                candidate_request_flow=candidate_request_flow,
            )
        )
        self._session._record_invocation_result(
            binding_id=self._binding_id,
            symbol_id=self._symbol.symbol_id,
            result=result,
        )
        return result


class VerifiedCompositionCrossing:
    """Verified mechanism-specific callable for a registered adapter crossing."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
        crossing: CompositionCrossingBinding,
        source_instance: object,
    ) -> None:
        target = crossing.symbol.resolve()
        self._session = session
        self._composition = composition
        self._crossing = crossing
        self._source_instance = source_instance
        self._target = target
        self._expected_definition = _callable_definition(target)
        self._identity_guard = session._callable_identity_guard(
            crossing.symbol,
            target,
        )
        self._result_reference = CrossingResultReference(
            composition_id=composition.composition_id,
            target_pathway_id=crossing.target_pathway_id,
        )
        self.__name__ = getattr(
            target,
            "__name__",
            crossing.symbol.qualified_symbol,
        )
        self.__doc__ = getattr(target, "__doc__", None)
        self.__signature__ = inspect.signature(target)

    @property
    def symbol_id(self) -> str:
        return self._crossing.symbol.symbol_id

    @property
    def result_reference(self) -> CrossingResultReference:
        """Return the deferred target-instance reference for endpoint links."""

        return self._result_reference

    @property
    def callable_identity(self) -> Mapping[str, Any]:
        return self._identity_guard.identity_record

    def _assert_current_callable(self) -> tuple[Callable[..., Any], Mapping[str, Any]]:
        symbol = self._crossing.symbol
        current = symbol.resolve()
        if (
            _callable_definition(current) is not self._expected_definition
            or _callable_definition(self._target) is not self._expected_definition
        ):
            raise SymbolBindingError(
                f"composition crossing {symbol.symbol_id!r} callable identity changed"
            )
        current_identity = self._identity_guard.assert_current(current)
        return current, current_identity

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        scope = self._session._assert_crossing_invocation_allowed(
            composition=self._composition,
            symbol_id=self.symbol_id,
        )
        target, callable_identity = self._assert_current_callable()
        effect_contract = self._session.authority.effect_outcome_contract(
            self.symbol_id
        )
        try:
            arguments = inspect.signature(target).bind(*args, **kwargs).arguments
        except TypeError as exc:
            raise SymbolBindingError(
                f"composition crossing {self.symbol_id!r} arguments are invalid"
            ) from exc
        source_argument = self._crossing.source_argument_name
        if arguments.get(source_argument) is not self._source_instance:
            raise SymbolBindingError(
                f"composition crossing {self.symbol_id!r} must consume the "
                "declared source instance"
            )
        pre_call_effect_evidence = (
            effect_contract.capture_pre_call_evidence(target)
            if effect_contract is not None
            else None
        )
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            self._session._record_crossing_invocation(
                scope,
                CrossingInvocationRecord(
                    crossing_scope_id=scope.scope_id,
                    binding_id=self._composition.binding_id,
                    composition_id=self._composition.composition_id,
                    symbol_id=self.symbol_id,
                    source_binding_id=self._composition.source_binding.binding_id,
                    target_binding_id=self._composition.target_binding.binding_id,
                    outcome="raised",
                    return_category=None,
                    effect_contract_id=(
                        effect_contract.contract_id
                        if effect_contract is not None
                        else None
                    ),
                    effect_kind=(
                        effect_contract.effect_kind
                        if effect_contract is not None
                        else "unreviewed"
                    ),
                    effect_outcome="unknown",
                    claim_qualifying_effect=False,
                    effect_evidence=None,
                    result_type=None,
                    error_type=type(exc).__name__,
                    callable_identity=callable_identity,
                ),
            )
            raise
        self._result_reference._set(result)
        (
            return_category,
            effect_contract_id,
            effect_kind,
            effect_outcome,
            claim_qualifying_effect,
            effect_evidence,
        ) = _classify_returned_effect(
            self._session.authority,
            self.symbol_id,
            result,
            target=target,
            pre_call_evidence=pre_call_effect_evidence,
        )
        self._session._record_crossing_invocation(
            scope,
            CrossingInvocationRecord(
                crossing_scope_id=scope.scope_id,
                binding_id=self._composition.binding_id,
                composition_id=self._composition.composition_id,
                symbol_id=self.symbol_id,
                source_binding_id=self._composition.source_binding.binding_id,
                target_binding_id=self._composition.target_binding.binding_id,
                outcome="returned",
                return_category=return_category,
                effect_contract_id=effect_contract_id,
                effect_kind=effect_kind,
                effect_outcome=effect_outcome,
                claim_qualifying_effect=claim_qualifying_effect,
                effect_evidence=effect_evidence,
                result_type=type(result).__name__,
                error_type=None,
                callable_identity=callable_identity,
            ),
        )
        return result


class BoundPathway:
    """An exact admitted pathway declaration and its stage links."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        pathway_id: str,
        stage_ids: Sequence[str],
        composition_ids: Sequence[str] = (),
    ) -> None:
        self._session = session
        self.binding_id = binding_id
        self.pathway_id = pathway_id
        self.stage_ids = tuple(stage_ids)
        self.composition_ids = tuple(composition_ids)

    @property
    def contract(self) -> Mapping[str, Any]:
        return self._session.authority.pathway(self.pathway_id)

    def symbol(
        self,
        stage_id: str,
        *,
        symbol_id: str | None = None,
        instance: (
            object
            | CrossingResultReference
            | FlowDerivedInstanceReference
            | None
        ) = None,
    ) -> VerifiedCallable:
        """Link one declared stage to an exact real source callable."""

        if (
            isinstance(instance, CrossingResultReference)
            and instance.target_pathway_id != self.pathway_id
        ):
            raise SymbolBindingError(
                f"crossing {instance.composition_id!r} returns "
                f"{instance.target_pathway_id!r}, not {self.pathway_id!r}"
            )
        if isinstance(instance, FlowDerivedInstanceReference) and (
            instance.target_binding_id != self.binding_id
            or instance.target_pathway_id != self.pathway_id
            or instance.target_stage_id != stage_id
        ):
            raise SymbolBindingError(
                f"flow-derived target for {instance.composition_id!r} requires "
                f"{instance.target_pathway_id}:{instance.target_stage_id}"
            )
        if stage_id not in self.stage_ids:
            raise SymbolBindingError(
                f"stage {stage_id!r} was not declared for binding {self.binding_id!r}"
            )
        symbols = self._session.authority.symbols(self.pathway_id, stage_id)
        if symbol_id is None:
            if len(symbols) != 1:
                choices = [symbol.symbol_id for symbol in symbols]
                raise SymbolBindingError(
                    f"stage {self.pathway_id}:{stage_id} requires an exact "
                    f"symbol_id choice from {choices}"
                )
            selected = symbols[0]
        else:
            matches = [symbol for symbol in symbols if symbol.symbol_id == symbol_id]
            if len(matches) != 1:
                raise SymbolBindingError(
                    f"symbol {symbol_id!r} is not registered for "
                    f"{self.pathway_id}:{stage_id}"
                )
            selected = matches[0]
        linked = VerifiedCallable(
            session=self._session,
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
            instance=instance,
        )
        self._session._register_link(
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
            instance=instance,
            callable_identity=linked.callable_identity,
        )
        return linked


class BoundComposition:
    """One exact executable matrix row and its endpoint pathway handles."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        composition: Mapping[str, Any],
        endpoints: Mapping[str, BoundPathway],
    ) -> None:
        self._session = session
        self.binding_id = binding_id
        self.composition_id = str(composition["composition_id"])
        self._composition = deepcopy(composition)
        self._endpoints = dict(endpoints)
        self._crossing_handle: VerifiedCompositionCrossing | None = None

    @property
    def contract(self) -> Mapping[str, Any]:
        return deepcopy(self._composition)

    @property
    def composition_status(self) -> str:
        return str(self._composition["composition_status"])

    @property
    def adapter_id(self) -> str:
        return str(self._composition["adapter_id"])

    @property
    def adapter_owner(self) -> str:
        return str(self._composition["adapter_owner"])

    @property
    def endpoint_bindings(self) -> tuple[BoundPathway, ...]:
        return tuple(self._endpoints.values())

    @property
    def source_binding(self) -> BoundPathway:
        return self.pathway(str(self._composition["from_pathway_id"]))

    @property
    def target_binding(self) -> BoundPathway:
        return self.pathway(str(self._composition["to_pathway_id"]))

    def pathway(self, pathway_id: str) -> BoundPathway:
        try:
            return self._endpoints[pathway_id]
        except KeyError as exc:
            raise UnknownPathwayError(
                f"{pathway_id!r} is not an endpoint of {self.composition_id}"
            ) from exc

    def crossing(
        self,
        *,
        source_instance: object,
    ) -> VerifiedCompositionCrossing:
        """Link the exact registered adapter callable for this composition."""

        self._session._require_declaration_phase()
        if self._crossing_handle is not None:
            raise CausalPathwayBindingError(
                f"composition {self.composition_id!r} crossing is already linked"
            )
        crossing = self._session.authority.composition_crossing(self.composition_id)
        handle = VerifiedCompositionCrossing(
            session=self._session,
            composition=self,
            crossing=crossing,
            source_instance=source_instance,
        )
        self._session._register_crossing_link(
            composition=self,
            crossing=crossing,
            source_instance=source_instance,
            result_reference=handle.result_reference,
            callable_identity=handle.callable_identity,
        )
        self._crossing_handle = handle
        return handle

    def flow_derived_target_instance(
        self,
        *,
        source: VerifiedCallable,
    ) -> FlowDerivedInstanceReference:
        """Declare a target owner whose state must derive from one source result."""

        self._session._require_declaration_phase()
        if self.composition_status == "lawful_with_explicit_adapter":
            raise BindingStateError(
                "explicit-adapter compositions must use their crossing result"
            )
        contract = composition_dataflow_contract(
            self.composition_id,
            explicit_adapter=False,
        )
        if not (
            contract["source_port"].startswith("result")
            and contract["target_port"].startswith("receiver")
            and contract["source_stage_id"] != "*"
            and contract["target_stage_id"] != "*"
        ):
            raise BindingStateError(
                f"composition {self.composition_id!r} has no flow-derived "
                "target-instance contract"
            )
        if (
            source._session is not self._session
            or source._binding_id != self.source_binding.binding_id
            or source._pathway_id != self.source_binding.pathway_id
            or source._stage_id != contract["source_stage_id"]
            or self.composition_id not in source._composition_ids
        ):
            raise SymbolBindingError(
                f"source handle is not the declared {self.composition_id!r} "
                "flow-contract source"
            )
        return FlowDerivedInstanceReference(
            session=self._session,
            composition=self,
            source_binding_id=source._binding_id,
            target_binding_id=self.target_binding.binding_id,
            target_pathway_id=self.target_binding.pathway_id,
            source_stage_id=source._stage_id,
            source_symbol_id=source.symbol_id,
            target_stage_id=contract["target_stage_id"],
            source_port=contract["source_port"],
            target_port=contract["target_port"],
        )

    def evidence_scope(self) -> CompositionExecutionScope:
        """Return an explicit provenance-only scope for one crossing use."""

        return CompositionExecutionScope(session=self._session, composition=self)


class CompositionExecutionScope:
    """Ordered observed-use scope; it does not dispatch composition mechanics."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
    ) -> None:
        self._session = session
        self.composition = composition
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._session._open_composition_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._session._close_composition_scope(self)
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
        self._session = session
        self.alternatives = alternatives
        self.scope_id = ""
        self._selected_pathway_id: str | None = None
        self._events: list[dict[str, Any]] = []
        self._invalid_pathway_id: str | None = None
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._session._open_alternative_selection_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None and self._invalid_pathway_id is None
        self._session._close_alternative_selection_scope(self)
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
        self._session = session
        self.candidate = candidate
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._mechanism_events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._session._open_candidate_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._session._close_candidate_scope(self)
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
            mechanism=self._session._candidate_mechanism(
                self.candidate.candidate_id
            ),
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


class BindingArtifact:
    """Immutable canonical JSON artifact with a content digest."""

    def __init__(self, record: Mapping[str, Any], *, digest_field: str) -> None:
        self._record = deepcopy(dict(record))
        self._digest_field = digest_field

    @property
    def digest(self) -> str:
        return str(self._record[self._digest_field])

    def to_record(self) -> dict[str, Any]:
        return deepcopy(self._record)

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.write_text(
            json.dumps(self._record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class BindingLock(BindingArtifact):
    """Exact pre-execution pathway declaration and claim envelope."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="lock_digest")

    def contains_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: Sequence[str],
    ) -> bool:
        """Return whether this lock freezes one exact callable link."""

        record = self.to_record()
        for binding in record["declared_pathway_bindings"]:
            if (
                binding["binding_id"] != binding_id
                or binding["pathway_id"] != pathway_id
                or binding["composition_ids"] != list(composition_ids)
            ):
                continue
            return any(
                link["stage_id"] == stage_id and link["symbol_id"] == symbol_id
                for link in binding["expected_concrete_symbols"]
            )
        return False

    def contains_crossing_link(
        self,
        *,
        binding_id: str,
        composition_id: str,
        symbol_id: str,
    ) -> bool:
        """Return whether the lock freezes one explicit crossing callable."""

        for binding in self.to_record()["declared_composition_bindings"]:
            crossing = binding.get("expected_crossing_callable")
            if (
                binding.get("binding_id") == binding_id
                and binding.get("composition_id") == composition_id
                and isinstance(crossing, dict)
                and crossing.get("symbol_id") == symbol_id
            ):
                return True
        return False

    def contains_candidate_mechanism_link(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> bool:
        """Return whether the lock freezes one exact candidate callable."""

        for candidate in self.to_record()["candidate_declarations"]:
            link = candidate.get("candidate_mechanism_link")
            if candidate.get("candidate_id") == candidate_id and isinstance(
                link, Mapping
            ):
                return link.get("symbol_id") == symbol_id
        return False


class BindingReceipt(BindingArtifact):
    """Exact post-use receipt linked to one binding lock."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="receipt_digest")


class PathwayBindingSession:
    """Explicit declaration and linkage session; it never selects semantics."""

    def __init__(self, authority: CausalPathwayAuthority) -> None:
        self.authority = authority
        self._phase = "declaration"
        self._pathway_bindings: dict[str, BoundPathway] = {}
        self._composition_bindings: dict[str, BoundComposition] = {}
        self._candidates: dict[str, CandidateDeclaration] = {}
        self._candidate_mechanism_handles: dict[
            str, VerifiedCandidateMechanism
        ] = {}
        self._alternatives: dict[str, AllowedPathwayAlternatives] = {}
        self._linked_symbols: dict[tuple[str, str], dict[str, Any]] = {}
        self._linked_instances: dict[
            tuple[str, str],
            object
            | CrossingResultReference
            | FlowDerivedInstanceReference
            | None,
        ] = {}
        self._direct_runtime_instances: list[object] = []
        self._runtime_flow_objects: list[object] = []
        self._crossing_links: dict[str, dict[str, Any]] = {}
        self._crossing_runtime_links: dict[
            str,
            tuple[object, CrossingResultReference],
        ] = {}
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
        self._candidate_uses: list[CandidateUseRecord] = []
        self._lock: BindingLock | None = None
        self._resolved_source_paths: dict[str, Path] = {}
        self._verified_source_files: dict[Path, _VerifiedSourceFile] = {}
        self._callable_identity_guards: dict[str, _CallableIdentityGuard] = {}

    def _callable_identity_guard(
        self,
        symbol: SourceSymbolBinding,
        target: Callable[..., Any],
    ) -> _CallableIdentityGuard:
        """Fully verify a symbol once and return its session-level guard."""

        existing = self._callable_identity_guards.get(symbol.symbol_id)
        if existing is not None:
            if existing.symbol != symbol:
                raise SymbolBindingError(
                    f"binding symbol {symbol.symbol_id!r} has conflicting identities"
                )
            existing.assert_current(target)
            return existing

        definition, module, qualified_symbol = symbol._validated_definition(target)
        expected_source = self._resolved_source_paths.get(symbol.source_path)
        if expected_source is None:
            expected_source = (
                self.authority.repository_root / symbol.source_path
            ).resolve()
            self._resolved_source_paths[symbol.source_path] = expected_source
        source = symbol._resolved_source_path(
            definition,
            self.authority.repository_root,
            expected_source=expected_source,
        )
        source_file = self._verified_source_files.get(source)
        if source_file is None:
            source_file = _VerifiedSourceFile.verify(
                source,
                expected_sha256=symbol.source_sha256,
            )
            self._verified_source_files[source] = source_file
        else:
            if source_file.expected_sha256 != symbol.source_sha256:
                raise SymbolBindingError(
                    f"binding source {source} has inconsistent expected digests"
                )
            source_file.assert_current()
        identity = symbol._identity_from_verified_source(
            definition,
            module=module,
            qualified_symbol=qualified_symbol,
        )
        source_file.assert_current()
        guard = _CallableIdentityGuard(
            symbol=symbol,
            expected_definition=definition,
            source_file=source_file,
            identity=identity,
            identity_record=MappingProxyType(identity.to_record()),
        )
        self._callable_identity_guards[symbol.symbol_id] = guard
        return guard

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def invocation_records(self) -> tuple[InvocationRecord, ...]:
        return tuple(self._invocations)

    @property
    def crossing_invocation_records(self) -> tuple[CrossingInvocationRecord, ...]:
        return tuple(self._crossing_invocations)

    @property
    def candidate_mechanism_invocation_records(
        self,
    ) -> tuple[CandidateMechanismInvocationRecord, ...]:
        return tuple(self._candidate_mechanism_invocations)

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
    def _state_surfaces(value: object | None) -> tuple[object | None, object | None]:
        """Expose only the established GRC/LGRC runtime state carriers."""

        if value is None:
            return None, None
        get_state = getattr(value, "get_state", None)
        if not callable(get_state):
            return None, None
        state = get_state()
        return state, getattr(state, "base_state", None)

    def _runtime_object_flow(
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
    def _attach_flow_derivation(
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

    @property
    def candidates(self) -> tuple[CandidateDeclaration, ...]:
        return tuple(self._candidates.values())

    def _candidate_evidence_scope(
        self,
        candidate: CandidateDeclaration,
    ) -> CandidateExecutionScope:
        """Create the runtime-owned evidence scope requested by a candidate."""

        return CandidateExecutionScope(session=self, candidate=candidate)

    def _candidate_mechanism(
        self,
        candidate_id: str,
    ) -> VerifiedCandidateMechanism:
        try:
            return self._candidate_mechanism_handles[candidate_id]
        except KeyError as exc:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} lacks executable mechanism evidence"
            ) from exc

    @property
    def alternatives(self) -> tuple[AllowedPathwayAlternatives, ...]:
        return tuple(self._alternatives.values())

    @property
    def binding_lock(self) -> BindingLock | None:
        return self._lock

    def _require_declaration_phase(self) -> None:
        if self._phase != "declaration":
            raise BindingStateError(
                f"binding declarations are closed in session phase {self._phase!r}"
            )

    def _register_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        composition_ids: tuple[str, ...],
        symbol: SourceSymbolBinding,
        instance: (
            object
            | CrossingResultReference
            | FlowDerivedInstanceReference
            | None
        ),
        callable_identity: Mapping[str, Any],
    ) -> None:
        self._require_declaration_phase()
        key = (binding_id, symbol.symbol_id)
        effect_contract = self.authority.effect_outcome_contract(symbol.symbol_id)
        runtime_instance_binding = self._runtime_instance_binding(
            instance,
            call_kind=symbol.call_kind,
        )
        self._linked_symbols[key] = {
            "binding_id": binding_id,
            "pathway_id": pathway_id,
            "stage_id": stage_id,
            "composition_ids": list(composition_ids),
            "symbol_id": symbol.symbol_id,
            "module": symbol.module,
            "qualified_symbol": symbol.qualified_symbol,
            "binding_role": symbol.binding_role,
            "call_kind": symbol.call_kind,
            "source_path": symbol.source_path,
            "source_sha256": symbol.source_sha256,
            "required_keyword_arguments": dict(symbol.required_keyword_arguments),
            "effect_outcome_contract": (
                effect_contract.to_record() if effect_contract is not None else None
            ),
            "runtime_instance_binding": runtime_instance_binding,
            "callable_identity": dict(callable_identity),
        }
        self._linked_instances[key] = instance

    def _runtime_instance_binding(
        self,
        instance: (
            object
            | CrossingResultReference
            | FlowDerivedInstanceReference
            | None
        ),
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

    def _register_crossing_link(
        self,
        *,
        composition: BoundComposition,
        crossing: CompositionCrossingBinding,
        source_instance: object,
        result_reference: CrossingResultReference,
        callable_identity: Mapping[str, Any],
    ) -> None:
        self._require_declaration_phase()
        if composition.binding_id in self._crossing_links:
            raise CausalPathwayBindingError(
                f"composition binding {composition.binding_id!r} already has a crossing"
            )
        symbol = crossing.symbol
        effect_contract = self.authority.effect_outcome_contract(symbol.symbol_id)
        self._crossing_links[composition.binding_id] = {
            "binding_id": composition.binding_id,
            "composition_id": composition.composition_id,
            "crossing_kind": crossing.crossing_kind,
            "source_binding_id": composition.source_binding.binding_id,
            "source_pathway_id": crossing.source_pathway_id,
            "source_argument_name": crossing.source_argument_name,
            "target_binding_id": composition.target_binding.binding_id,
            "target_pathway_id": crossing.target_pathway_id,
            "symbol_id": symbol.symbol_id,
            "module": symbol.module,
            "qualified_symbol": symbol.qualified_symbol,
            "binding_role": symbol.binding_role,
            "call_kind": symbol.call_kind,
            "source_path": symbol.source_path,
            "source_sha256": symbol.source_sha256,
            "effect_outcome_contract": (
                effect_contract.to_record() if effect_contract is not None else None
            ),
            "callable_identity": dict(callable_identity),
        }
        self._crossing_runtime_links[composition.binding_id] = (
            source_instance,
            result_reference,
        )

    def _assert_invocation_allowed(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: tuple[str, ...],
    ) -> None:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "claim-bearing bound calls require a frozen pre-execution lock"
            )
        if not self._lock.contains_link(
            binding_id=binding_id,
            pathway_id=pathway_id,
            stage_id=stage_id,
            symbol_id=symbol_id,
            composition_ids=composition_ids,
        ):
            raise BindingStateError(
                f"symbol {symbol_id!r} is absent from binding lock {self._lock.digest}"
            )
        if self._active_alternative_selection_scope is not None:
            self._active_alternative_selection_scope._assert_pathway_allowed(pathway_id)

    def _candidate_target_request_flow(
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

    def _record_invocation(self, record: InvocationRecord) -> None:
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

    def _record_invocation_result(
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
        state, base_state = PathwayBindingSession._state_surfaces(value)
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

    def _bind_flow_derived_instance(
        self,
        *,
        reference: FlowDerivedInstanceReference,
        source_result: object,
        target_instance: object,
    ) -> None:
        """Validate and bind one consumer-created target to exact live object flow."""

        scope = self._active_composition_scope
        if self._phase != "locked" or self._lock is None or scope is None:
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
        source_carrier = self._live_flow_port(
            source_result,
            reference.source_port,
        )
        target_carrier = self._live_flow_port(
            target_instance,
            reference.target_port,
        )
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
                "contract_id": (
                    f"{reference.composition_id}:runtime-object-flow:v1"
                ),
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

    def _record_crossing_invocation(
        self,
        scope: CompositionExecutionScope,
        record: CrossingInvocationRecord,
    ) -> None:
        invocation_index = len(self._crossing_invocations)
        record = replace(
            record,
            execution_event_order=self._execution_event_count,
        )
        self._crossing_invocations.append(record)
        scope._record_crossing(
            event_order=self._execution_event_count,
            invocation_index=invocation_index,
            record=record,
        )
        self._execution_event_count += 1

    def _record_candidate_mechanism_invocation(
        self,
        scope: CandidateExecutionScope,
        record: CandidateMechanismInvocationRecord,
        *,
        result: object | None,
    ) -> None:
        invocation_index = len(self._candidate_mechanism_invocations)
        record = replace(
            record,
            execution_event_order=self._execution_event_count,
        )
        self._candidate_mechanism_invocations.append(record)
        scope._record_mechanism(
            event_order=self._execution_event_count,
            invocation_index=invocation_index,
            record=record,
            result=result,
        )
        self._execution_event_count += 1

    def _record_candidate_mechanism_event(
        self,
        scope: Any,
        event: _CandidateMechanismEvent,
        *,
        result: object | None,
    ) -> None:
        """Adapt a candidate-owned event to the runtime invocation ledger."""

        self._record_candidate_mechanism_invocation(
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

    def _open_composition_scope(self, scope: CompositionExecutionScope) -> str:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "composition evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        if scope.composition.binding_id not in self._composition_bindings:
            raise BindingStateError("composition scope is not declared in this session")
        scope_id = (
            f"{scope.composition.binding_id}:crossing-scope:"
            f"{len(self._composition_scopes)}"
        )
        self._active_composition_scope = scope
        self._composition_scopes.append(scope)
        return scope_id

    def _close_composition_scope(self, scope: CompositionExecutionScope) -> None:
        if self._active_composition_scope is not scope:
            raise BindingStateError("composition evidence scope is not active")
        self._active_composition_scope = None

    def _open_candidate_scope(self, scope: CandidateExecutionScope) -> str:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "candidate evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        candidate = self._candidates.get(scope.candidate.candidate_id)
        if candidate is not scope.candidate:
            raise BindingStateError("candidate scope is not declared in this session")
        scope_id = (
            f"candidate:{scope.candidate.candidate_id}:evidence-scope:"
            f"{len(self._candidate_scopes)}"
        )
        self._active_candidate_scope = scope
        self._candidate_scopes.append(scope)
        return scope_id

    def _close_candidate_scope(self, scope: CandidateExecutionScope) -> None:
        if self._active_candidate_scope is not scope:
            raise BindingStateError("candidate evidence scope is not active")
        self._active_candidate_scope = None

    def _open_alternative_selection_scope(
        self,
        scope: AlternativeSelectionScope,
    ) -> str:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "alternative selection scopes require a frozen binding lock"
            )
        if self._active_alternative_selection_scope is not None:
            raise BindingStateError("alternative selection scopes cannot overlap")
        alternatives = self._alternatives.get(scope.alternatives.alternative_set_id)
        if alternatives is not scope.alternatives:
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

    def _close_alternative_selection_scope(
        self,
        scope: AlternativeSelectionScope,
    ) -> None:
        if self._active_alternative_selection_scope is not scope:
            raise BindingStateError("alternative selection scope is not active")
        self._active_alternative_selection_scope = None

    def _assert_crossing_invocation_allowed(
        self,
        *,
        composition: BoundComposition,
        symbol_id: str,
    ) -> CompositionExecutionScope:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "composition crossing calls require a frozen binding lock"
            )
        scope = self._active_composition_scope
        if scope is None or scope.composition is not composition:
            raise BindingStateError(
                "composition crossing calls require their explicit evidence scope"
            )
        if not self._lock.contains_crossing_link(
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

    def _assert_candidate_mechanism_invocation_allowed(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> CandidateExecutionScope:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "candidate mechanism calls require a frozen binding lock"
            )
        scope = self._active_candidate_scope
        if scope is None or scope.candidate.candidate_id != candidate_id:
            raise BindingStateError(
                "candidate mechanism calls require their explicit evidence scope"
            )
        if not self._lock.contains_candidate_mechanism_link(
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

    def _all_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        endpoints = (
            endpoint
            for composition in self._composition_bindings.values()
            for endpoint in composition.endpoint_bindings
        )
        return (*self._pathway_bindings.values(), *endpoints)

    def _binding_record(self, binding: BoundPathway) -> dict[str, Any]:
        contract = self.authority.pathway(binding.pathway_id)
        expected_symbols = sorted(
            (
                deepcopy(link)
                for (binding_id, _), link in self._linked_symbols.items()
                if binding_id == binding.binding_id
            ),
            key=lambda item: str(item["symbol_id"]),
        )
        return {
            "binding_id": binding.binding_id,
            "pathway_id": binding.pathway_id,
            "declared_stage_ids": list(binding.stage_ids),
            "composition_ids": list(binding.composition_ids),
            "mechanism_ownership": contract["mechanism_ownership"],
            "availability": contract["availability"],
            "activation": contract["activation"],
            "configured_residue": list(contract["configured_residue"]),
            "producer_residue": list(contract["producer_residue"]),
            "expected_concrete_symbols": expected_symbols,
        }

    def _composition_record(self, binding: BoundComposition) -> dict[str, Any]:
        contract = binding.contract
        explicit_adapter = (
            contract["composition_status"] == "lawful_with_explicit_adapter"
        )
        dataflow_requirement = (
            EXPLICIT_ADAPTER_DATAFLOW
            if explicit_adapter
            else ATTESTED_OBJECT_FLOW_DATAFLOW
        )
        return {
            "binding_id": binding.binding_id,
            "composition_id": binding.composition_id,
            "from_pathway_id": contract["from_pathway_id"],
            "from_stage_ids": list(contract["from_stage_ids"]),
            "to_pathway_id": contract["to_pathway_id"],
            "to_stage_ids": list(contract["to_stage_ids"]),
            "composition_status": contract["composition_status"],
            "adapter_id": contract["adapter_id"],
            "adapter_owner": contract["adapter_owner"],
            "authority_retained": list(contract["authority_retained"]),
            "authority_transferred": list(contract["authority_transferred"]),
            "information_lost_or_compressed": contract[
                "information_lost_or_compressed"
            ],
            "claim_ceiling": contract["claim_ceiling"],
            "blocked_relabels": list(contract["blocked_relabels"]),
            "runtime_dataflow_requirement": dataflow_requirement,
            "runtime_dataflow_contract": composition_dataflow_contract(
                binding.composition_id,
                explicit_adapter=explicit_adapter,
            ),
            "expected_crossing_callable": deepcopy(
                self._crossing_links.get(binding.binding_id)
            ),
        }

    def _derive_claim_envelope(
        self,
        *,
        pathway_bindings: Sequence[BoundPathway],
        composition_bindings: Sequence[BoundComposition],
        candidates: Sequence[CandidateDeclaration],
    ) -> dict[str, Any]:
        pathway_claims: list[dict[str, Any]] = []
        composition_claims: list[dict[str, Any]] = []
        producer_cuts: list[dict[str, Any]] = []
        adapter_cuts: list[dict[str, Any]] = []
        diagnostic_relations: list[dict[str, str]] = []
        configured_semantics: list[dict[str, Any]] = []
        blocked_claims: list[str] = []

        for pathway_binding in sorted(
            pathway_bindings, key=lambda item: item.binding_id
        ):
            contract = self.authority.pathway(pathway_binding.pathway_id)
            pathway_claims.append(
                {
                    "binding_id": pathway_binding.binding_id,
                    "pathway_id": pathway_binding.pathway_id,
                    "constituent_claim_ceiling": list(contract["supported_claims"]),
                    "mechanism_ownership": contract["mechanism_ownership"],
                    "required_qualifiers": {
                        "configured_residue": list(contract["configured_residue"]),
                        "producer_residue": list(contract["producer_residue"]),
                        "naturalization_debt": list(contract["naturalization_debt"]),
                    },
                    "blocked_claims": list(contract["blocked_claims"]),
                }
            )
            if contract["configured_residue"]:
                configured_semantics.append(
                    {
                        "pathway_id": pathway_binding.pathway_id,
                        "residue": list(contract["configured_residue"]),
                    }
                )
            if (
                contract["producer_residue"]
                or contract["mechanism_ownership"] == "producer"
            ):
                producer_cuts.append(
                    {
                        "pathway_id": pathway_binding.pathway_id,
                        "producer_identity": contract["trigger_surface"],
                        "producer_owned_authorities": list(
                            contract["producer_residue"]
                        ),
                    }
                )
            if contract["mechanism_ownership"] == "diagnostic":
                diagnostic_relations.append(
                    {
                        "kind": "pathway",
                        "identity": pathway_binding.pathway_id,
                    }
                )
            blocked_claims.extend(str(item) for item in contract["blocked_claims"])

        for composition_binding in sorted(
            composition_bindings,
            key=lambda item: (item.composition_id, item.binding_id),
        ):
            contract = composition_binding.contract
            status = str(contract["composition_status"])
            composition_claims.append(
                {
                    "binding_id": composition_binding.binding_id,
                    "composition_id": composition_binding.composition_id,
                    "composition_status": status,
                    "constituent_claim_ceiling": contract["claim_ceiling"],
                    "adapter_id": contract["adapter_id"],
                    "adapter_owner": contract["adapter_owner"],
                    "authority_retained": list(contract["authority_retained"]),
                    "authority_transferred": list(contract["authority_transferred"]),
                    "blocked_claims": list(contract["blocked_relabels"]),
                }
            )
            if status == "producer_mediated":
                producer_cuts.append(
                    {
                        "composition_id": composition_binding.composition_id,
                        "producer_identity": contract["adapter_id"],
                        "producer_owner": contract["adapter_owner"],
                        "producer_owned_authorities": list(
                            contract["authority_transferred"]
                        ),
                    }
                )
            if status == "lawful_with_explicit_adapter":
                adapter_cuts.append(
                    {
                        "composition_id": composition_binding.composition_id,
                        "adapter_id": contract["adapter_id"],
                        "adapter_owner": contract["adapter_owner"],
                    }
                )
            if status == "diagnostic_only":
                diagnostic_relations.append(
                    {
                        "kind": "composition",
                        "identity": composition_binding.composition_id,
                    }
                )
            blocked_claims.extend(str(item) for item in contract["blocked_relabels"])

        ordered_candidates = sorted(
            candidates,
            key=lambda item: item.candidate_id,
        )
        candidate_records = [candidate.to_record() for candidate in ordered_candidates]
        for candidate in ordered_candidates:
            blocked_claims.extend(candidate.blocked_claims)
        if candidates:
            overall_status = "experimental_unregistered"
        elif diagnostic_relations:
            overall_status = "bounded_with_diagnostic_cut"
        elif producer_cuts or adapter_cuts:
            overall_status = "bounded_with_explicit_ownership_cuts"
        else:
            overall_status = "admitted_bounded"
        return {
            "constituent_pathway_claim_ceilings": pathway_claims,
            "constituent_composition_claim_ceilings": composition_claims,
            "required_qualifiers": {
                "configured_semantics": configured_semantics,
                "producer_cuts": producer_cuts,
                "adapter_cuts": adapter_cuts,
                "diagnostic_only_relations": diagnostic_relations,
                "candidate_relations": candidate_records,
            },
            "contains_producer_cut": bool(producer_cuts),
            "contains_adapter_cut": bool(adapter_cuts),
            "contains_diagnostic_only_relation": bool(diagnostic_relations),
            "experimental_unregistered": bool(candidates),
            "blocked_claims": list(dict.fromkeys(blocked_claims)),
            "overall_claim_status": overall_status,
            "composition_status_is_maturity_score": False,
            "synthesized_chain_claim": False,
        }

    def _validate_explicit_crossing_dataflow(self) -> None:
        """Bind explicit-adapter endpoints to the adapter's exact object flow."""

        for composition in self._composition_bindings.values():
            if composition.composition_status != "lawful_with_explicit_adapter":
                continue
            try:
                source_instance, result_reference = self._crossing_runtime_links[
                    composition.binding_id
                ]
            except KeyError as exc:
                raise BindingStateError(
                    f"explicit-adapter composition {composition.composition_id!r} "
                    "lacks a crossing runtime link"
                ) from exc
            endpoint_roles = (
                (
                    composition.source_binding,
                    source_instance,
                    "declared_adapter_source_instance",
                ),
                (
                    composition.target_binding,
                    result_reference,
                    "adapter_result_reference",
                ),
            )
            for endpoint, expected_instance, role in endpoint_roles:
                for key, link in self._linked_symbols.items():
                    if key[0] != endpoint.binding_id:
                        continue
                    if link["call_kind"] != "instance_method":
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            "requires instance-bound stage symbols"
                        )
                    if self._linked_instances.get(key) is not expected_instance:
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            f"must use its {role.replace('_', ' ')}"
                        )
                    link["composition_crossing_instance_role"] = role
            crossing_link = self._crossing_links[composition.binding_id]
            crossing_link["source_instance_binding"] = (
                "exact_declared_adapter_source_instance"
            )
            crossing_link["target_instance_binding"] = "exact_adapter_result_reference"

    def freeze_lock(self) -> BindingLock:
        """Close declarations and freeze exact symbols before execution."""

        self._require_declaration_phase()
        self.authority.assert_current()
        bindings = self._all_pathway_bindings()
        missing_crossings = sorted(
            binding.composition_id
            for binding in self._composition_bindings.values()
            if binding.composition_status == "lawful_with_explicit_adapter"
            and binding.binding_id not in self._crossing_links
        )
        if missing_crossings:
            raise BindingStateError(
                "explicit-adapter compositions require their exact crossing "
                f"callable before lock: {missing_crossings}"
            )
        self._validate_explicit_crossing_dataflow()
        for candidate in self._candidates.values():
            if candidate.mechanism_evidence is not None:
                candidate.mechanism_evidence.assert_current(
                    self.authority.repository_root,
                    candidate_kind=candidate.candidate_kind,
                    proposed_source_pathway_id=(candidate.proposed_source_pathway_id),
                    proposed_target_pathway_id=(candidate.proposed_target_pathway_id),
                    proposed_relation=candidate.proposed_relation,
                )
        declared_pathway_ids = {binding.pathway_id for binding in bindings}
        for alternatives in self._alternatives.values():
            missing = sorted(set(alternatives.pathway_ids) - declared_pathway_ids)
            if missing:
                raise BindingStateError(
                    f"alternative set {alternatives.alternative_set_id!r} lacks "
                    f"declared pathway bindings for {missing}"
                )
        claim_envelope = self._derive_claim_envelope(
            pathway_bindings=bindings,
            composition_bindings=tuple(self._composition_bindings.values()),
            candidates=tuple(self._candidates.values()),
        )
        record: dict[str, Any] = {
            "artifact": "causal-pathways-binding-lock",
            "schema_version": "causal_pathways_binding_lock_v1",
            **dict(self.authority.artifact_identities()),
            "declared_pathway_bindings": [
                self._binding_record(binding)
                for binding in sorted(bindings, key=lambda item: item.binding_id)
            ],
            "declared_composition_bindings": [
                self._composition_record(binding)
                for binding in sorted(
                    self._composition_bindings.values(),
                    key=lambda item: item.composition_id,
                )
            ],
            "allowed_pathway_alternatives": [
                {
                    "alternative_set_id": item.alternative_set_id,
                    "pathway_ids": list(item.pathway_ids),
                    "selection_authority": item.selection_authority,
                }
                for item in sorted(
                    self._alternatives.values(),
                    key=lambda item: item.alternative_set_id,
                )
            ],
            "candidate_declarations": [
                item.to_record()
                for item in sorted(
                    self._candidates.values(), key=lambda item: item.candidate_id
                )
            ],
            "explicit_producers": deepcopy(
                claim_envelope["required_qualifiers"]["producer_cuts"]
            ),
            "explicit_adapters": deepcopy(
                claim_envelope["required_qualifiers"]["adapter_cuts"]
            ),
            "pre_execution_claim_envelope": claim_envelope,
            "blocked_claims": list(claim_envelope["blocked_claims"]),
            "execution_transcript_trust_requirement": (
                EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
            ),
            "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
            "whole_run_causal_closure_claimed": False,
            "untracked_execution_observable_by_binding_plane": False,
            "semantic_selection_performed_by_binder": False,
            "unregistered_relation_bound_without_candidate": False,
            "lock_digest": "",
        }
        record["lock_digest"] = canonical_digest(record, excluding="lock_digest")
        self._lock = BindingLock(record)
        self._phase = "locked"
        return self._lock

    def record_candidate_use(
        self,
        candidate_id: str,
    ) -> CandidateUseRecord:
        """Record one scoped use of the frozen candidate executable."""

        if self._phase != "locked":
            raise BindingStateError("candidate use requires a frozen binding lock")
        if candidate_id not in self._candidates:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} was not declared before lock"
            )
        if any(item.candidate_id == candidate_id for item in self._candidate_uses):
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} already has a use record"
            )
        candidate = self._candidates[candidate_id]
        evidence = candidate.mechanism_evidence
        if evidence is None:
            raise InvalidCandidateError(
                "candidate use requires executable mechanism evidence "
                "declared before lock"
            )
        evidence.assert_current(
            self.authority.repository_root,
            candidate_kind=candidate.candidate_kind,
            proposed_source_pathway_id=candidate.proposed_source_pathway_id,
            proposed_target_pathway_id=candidate.proposed_target_pathway_id,
            proposed_relation=candidate.proposed_relation,
        )
        witnesses = [
            witness
            for scope in self._candidate_scopes
            if scope.candidate is candidate
            if (witness := scope.exercise_witness()) is not None
        ]
        if len(witnesses) != 1:
            raise InvalidCandidateError(
                "candidate use requires exactly one completed evidence scope with "
                "returned candidate-mechanism execution"
            )
        use = CandidateUseRecord(
            candidate_id=candidate_id,
            mechanism_evidence=MappingProxyType(evidence.to_record()),
            execution_witness=MappingProxyType(deepcopy(witnesses[0])),
        )
        self._candidate_uses.append(use)
        return use

    def _composition_witnesses(self) -> tuple[dict[str, Any], ...]:
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

    def _alternative_selection_witnesses(self) -> tuple[dict[str, Any], ...]:
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

    def _exercised_compositions(
        self,
        witnesses: Sequence[Mapping[str, Any]],
    ) -> tuple[BoundComposition, ...]:
        witnessed_binding_ids = {str(witness["binding_id"]) for witness in witnesses}
        return tuple(
            binding
            for binding in self._composition_bindings.values()
            if binding.binding_id in witnessed_binding_ids
        )

    def _actual_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        successful_binding_ids = {
            record.binding_id
            for record in self._invocations
            if record.claim_qualifying_effect
        }
        return tuple(
            binding
            for binding in self._all_pathway_bindings()
            if binding.binding_id in successful_binding_ids
        )

    def _use_graph(
        self,
        *,
        actual_bindings: Sequence[BoundPathway],
        exercised_compositions: Sequence[BoundComposition],
    ) -> dict[str, Any]:
        successful = [
            record for record in self._invocations if record.claim_qualifying_effect
        ]
        nodes: list[dict[str, Any]] = []
        for pathway_binding in sorted(
            actual_bindings, key=lambda item: item.binding_id
        ):
            contract = self.authority.pathway(pathway_binding.pathway_id)
            uses = [
                record
                for record in successful
                if record.binding_id == pathway_binding.binding_id
            ]
            nodes.append(
                {
                    "node_id": pathway_binding.binding_id,
                    "node_kind": "admitted_pathway",
                    "pathway_id": pathway_binding.pathway_id,
                    "pathway_status": {
                        "availability": contract["availability"],
                        "activation": contract["activation"],
                        "staleness_state": contract["staleness_state"],
                        "mechanism_ownership": contract["mechanism_ownership"],
                    },
                    "stage_ids_used": list(
                        dict.fromkeys(record.stage_id for record in uses)
                    ),
                    "mechanism_ownership": contract["mechanism_ownership"],
                    "configured_residue": list(contract["configured_residue"]),
                    "producer_residue": list(contract["producer_residue"]),
                    "source_bindings_used": list(
                        dict.fromkeys(record.symbol_id for record in uses)
                    ),
                }
            )
        edges: list[dict[str, Any]] = []
        for composition_binding in sorted(
            exercised_compositions, key=lambda item: item.composition_id
        ):
            contract = composition_binding.contract
            endpoint_ids = {
                endpoint.pathway_id: endpoint.binding_id
                for endpoint in composition_binding.endpoint_bindings
            }
            edges.append(
                {
                    "edge_id": composition_binding.binding_id,
                    "edge_kind": "registered_composition",
                    "composition_id": composition_binding.composition_id,
                    "source_node_id": endpoint_ids[str(contract["from_pathway_id"])],
                    "target_node_id": endpoint_ids[str(contract["to_pathway_id"])],
                    "composition_status": contract["composition_status"],
                    "adapter_id": contract["adapter_id"],
                    "adapter_owner": contract["adapter_owner"],
                    "producer_owner": (
                        contract["adapter_owner"]
                        if contract["composition_status"] == "producer_mediated"
                        else None
                    ),
                    "authority_retained": list(contract["authority_retained"]),
                    "authority_transferred": list(contract["authority_transferred"]),
                    "information_lost_or_compressed": contract[
                        "information_lost_or_compressed"
                    ],
                    "claim_ceiling": contract["claim_ceiling"],
                    "blocked_claims": list(contract["blocked_relabels"]),
                }
            )
        actual_by_pathway: dict[str, str] = {}
        for binding in actual_bindings:
            actual_by_pathway.setdefault(binding.pathway_id, binding.binding_id)
        for use in self._candidate_uses:
            candidate = self._candidates[use.candidate_id]
            if candidate.candidate_kind == "pathway":
                nodes.append(
                    {
                        "node_id": f"candidate:{candidate.candidate_id}",
                        "node_kind": "experimental_unregistered_candidate",
                        "candidate_id": candidate.candidate_id,
                        "claim_ceiling": candidate.claim_ceiling,
                        "promotion_status": candidate.promotion_status,
                        "mechanism_evidence": dict(use.mechanism_evidence),
                        "candidate_mechanism_link": dict(
                            candidate.mechanism_link or {}
                        ),
                        "candidate_execution_witness": dict(use.execution_witness),
                        "authority": dict(candidate.authority),
                        "producer_residue": list(candidate.producer_residue),
                        "adapter_residue": list(candidate.adapter_residue),
                        "configured_residue": list(candidate.configured_residue),
                        "invalid_relabel_conflict_ids": list(
                            candidate.invalid_relabel_conflict_ids
                        ),
                        "invalid_relabel_blocked_claims": list(
                            candidate.invalid_relabel_blocked_claims
                        ),
                        "invalid_relabel_relation_review": (
                            candidate.invalid_relabel_relation_review.to_record()
                            if candidate.invalid_relabel_relation_review is not None
                            else None
                        ),
                        "invalid_relabel_relation_review_trust_requirement": (
                            INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
                            if candidate.invalid_relabel_relation_review is not None
                            else None
                        ),
                        "blocked_claims": list(candidate.blocked_claims),
                    }
                )
                continue
            assert candidate.proposed_source_pathway_id is not None
            assert candidate.proposed_target_pathway_id is not None
            source_binding_id = str(use.execution_witness.get("source_binding_id", ""))
            target_binding_id = str(use.execution_witness.get("target_binding_id", ""))
            if (
                candidate.proposed_source_pathway_id not in actual_by_pathway
                or candidate.proposed_target_pathway_id not in actual_by_pathway
                or source_binding_id
                not in {binding.binding_id for binding in actual_bindings}
                or target_binding_id
                not in {binding.binding_id for binding in actual_bindings}
            ):
                raise BindingStateError(
                    f"used candidate {candidate.candidate_id!r} lacks actual bound "
                    "source or target pathway use"
                )
            edges.append(
                {
                    "edge_id": f"candidate:{candidate.candidate_id}",
                    "edge_kind": "experimental_unregistered_candidate",
                    "candidate_id": candidate.candidate_id,
                    "source_node_id": source_binding_id,
                    "target_node_id": target_binding_id,
                    "proposed_relation": candidate.proposed_relation,
                    "proposed_relation_claim_status": (
                        "descriptive_unreviewed_not_claim_qualified"
                    ),
                    "claim_ceiling": candidate.claim_ceiling,
                    "promotion_status": candidate.promotion_status,
                    "mechanism_evidence": dict(use.mechanism_evidence),
                    "candidate_mechanism_link": dict(
                        candidate.mechanism_link or {}
                    ),
                    "candidate_execution_witness": dict(use.execution_witness),
                    "authority": dict(candidate.authority),
                    "producer_residue": list(candidate.producer_residue),
                    "adapter_residue": list(candidate.adapter_residue),
                    "configured_residue": list(candidate.configured_residue),
                    "invalid_relabel_conflict_ids": list(
                        candidate.invalid_relabel_conflict_ids
                    ),
                    "invalid_relabel_blocked_claims": list(
                        candidate.invalid_relabel_blocked_claims
                    ),
                    "invalid_relabel_relation_review": (
                        candidate.invalid_relabel_relation_review.to_record()
                        if candidate.invalid_relabel_relation_review is not None
                        else None
                    ),
                    "invalid_relabel_relation_review_trust_requirement": (
                        INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
                        if candidate.invalid_relabel_relation_review is not None
                        else None
                    ),
                    "blocked_claims": list(candidate.blocked_claims),
                }
            )
        return {
            "nodes": nodes,
            "edges": edges,
            "unregistered_edge_synthesized_from_endpoint_co_use": False,
            "larger_chain_claim_synthesized": False,
        }

    def build_receipt(self) -> BindingReceipt:
        """Seal actual use against the exact frozen binding lock."""

        if self._phase != "locked" or self._lock is None:
            raise BindingStateError("a receipt requires one active binding lock")
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
        self.authority.assert_current()
        actual_bindings = self._actual_pathway_bindings()
        composition_witnesses = self._composition_witnesses()
        alternative_selection_witnesses = self._alternative_selection_witnesses()
        exercised_compositions = self._exercised_compositions(composition_witnesses)
        used_candidate_ids = {item.candidate_id for item in self._candidate_uses}
        used_candidates = tuple(
            self._candidates[candidate_id]
            for candidate_id in sorted(used_candidate_ids)
        )
        witnessed_candidate_mechanisms = {
            int(item.execution_witness["candidate_mechanism_invocation_index"])
            for item in self._candidate_uses
        }
        returned_candidate_mechanisms = {
            index
            for index, item in enumerate(self._candidate_mechanism_invocations)
            if item.outcome == "returned"
        }
        if witnessed_candidate_mechanisms != returned_candidate_mechanisms:
            raise BindingStateError(
                "returned candidate mechanisms require exact candidate-use witnesses"
            )
        for candidate in used_candidates:
            assert candidate.mechanism_evidence is not None
            candidate.mechanism_evidence.assert_current(
                self.authority.repository_root,
                candidate_kind=candidate.candidate_kind,
                proposed_source_pathway_id=candidate.proposed_source_pathway_id,
                proposed_target_pathway_id=candidate.proposed_target_pathway_id,
                proposed_relation=candidate.proposed_relation,
            )
        graph = self._use_graph(
            actual_bindings=actual_bindings,
            exercised_compositions=exercised_compositions,
        )
        claim_envelope = self._derive_claim_envelope(
            pathway_bindings=actual_bindings,
            composition_bindings=exercised_compositions,
            candidates=used_candidates,
        )
        successful_binding_ids = {binding.binding_id for binding in actual_bindings}
        all_bindings = self._all_pathway_bindings()
        declared_but_unused = {
            "pathway_binding_ids": sorted(
                binding.binding_id
                for binding in all_bindings
                if binding.binding_id not in successful_binding_ids
            ),
            "composition_binding_ids": sorted(
                binding.binding_id
                for binding in self._composition_bindings.values()
                if binding not in exercised_compositions
            ),
            "candidate_ids": sorted(set(self._candidates) - used_candidate_ids),
        }
        actual_uses = [
            {
                "invocation_index": index,
                "binding_id": item.binding_id,
                "pathway_id": item.pathway_id,
                "stage_id": item.stage_id,
                "symbol_id": item.symbol_id,
                "composition_ids": list(item.composition_ids),
                "outcome": item.outcome,
                "return_category": item.return_category,
                "effect_contract_id": item.effect_contract_id,
                "effect_kind": item.effect_kind,
                "effect_outcome": item.effect_outcome,
                "claim_qualifying_effect": item.claim_qualifying_effect,
                "effect_evidence": (
                    None
                    if item.effect_evidence is None
                    else dict(item.effect_evidence)
                ),
                "result_type": item.result_type,
                "error_type": item.error_type,
                "callable_identity": dict(item.callable_identity),
                "runtime_object_flow": deepcopy(item.runtime_object_flow),
                "candidate_request_flow": (
                    None
                    if item.candidate_request_flow is None
                    else deepcopy(item.candidate_request_flow)
                ),
                "execution_event_order": item.execution_event_order,
                "crossing_scope_id": item.crossing_scope_id,
                "candidate_scope_id": item.candidate_scope_id,
                "alternative_selection_scope_id": (item.alternative_selection_scope_id),
            }
            for index, item in enumerate(self._invocations)
        ]
        crossing_uses = [
            {
                "crossing_invocation_index": index,
                "crossing_scope_id": item.crossing_scope_id,
                "binding_id": item.binding_id,
                "composition_id": item.composition_id,
                "symbol_id": item.symbol_id,
                "source_binding_id": item.source_binding_id,
                "target_binding_id": item.target_binding_id,
                "outcome": item.outcome,
                "return_category": item.return_category,
                "effect_contract_id": item.effect_contract_id,
                "effect_kind": item.effect_kind,
                "effect_outcome": item.effect_outcome,
                "claim_qualifying_effect": item.claim_qualifying_effect,
                "effect_evidence": (
                    None
                    if item.effect_evidence is None
                    else dict(item.effect_evidence)
                ),
                "result_type": item.result_type,
                "error_type": item.error_type,
                "callable_identity": dict(item.callable_identity),
                "execution_event_order": item.execution_event_order,
            }
            for index, item in enumerate(self._crossing_invocations)
        ]
        candidate_mechanism_uses = [
            {
                "candidate_mechanism_invocation_index": index,
                "candidate_scope_id": item.candidate_scope_id,
                "candidate_id": item.candidate_id,
                "mechanism_id": item.mechanism_id,
                "symbol_id": item.symbol_id,
                "outcome": item.outcome,
                "result_type": item.result_type,
                "error_type": item.error_type,
                "callable_identity": dict(item.callable_identity),
                "relation_review_digest": item.relation_review_digest,
                "structural_result_observed": item.structural_result_observed,
                "runtime_object_flow": deepcopy(item.runtime_object_flow),
                "execution_event_order": item.execution_event_order,
            }
            for index, item in enumerate(self._candidate_mechanism_invocations)
        ]
        transcript_digest = execution_transcript_digest(
            binding_lock_digest=self._lock.digest,
            stage_invocations=actual_uses,
            crossing_invocations=crossing_uses,
            candidate_mechanism_invocations=candidate_mechanism_uses,
        )
        alternative_uses: list[dict[str, Any]] = []
        for alternatives in sorted(
            self._alternatives.values(),
            key=lambda item: item.alternative_set_id,
        ):
            scopes = [
                witness
                for witness in alternative_selection_witnesses
                if witness["alternative_set_id"] == alternatives.alternative_set_id
            ]
            qualifying_pathway_ids = [
                str(witness["selected_pathway_id"])
                for witness in scopes
                if witness["claim_qualifying_invocation_indices"]
            ]
            alternative_uses.append(
                {
                    "alternative_set_id": alternatives.alternative_set_id,
                    "selection_authority": alternatives.selection_authority,
                    "allowed_pathway_ids": list(alternatives.pathway_ids),
                    "selected_pathway_ids": list(
                        dict.fromkeys(
                            str(witness["selected_pathway_id"]) for witness in scopes
                        )
                    ),
                    "actual_pathway_ids_used": list(
                        dict.fromkeys(qualifying_pathway_ids)
                    ),
                    "selection_scopes": [deepcopy(witness) for witness in scopes],
                }
            )
        record: dict[str, Any] = {
            "artifact": "causal-pathways-binding-receipt",
            "schema_version": "causal_pathways_binding_receipt_v1",
            "binding_lock_digest": self._lock.digest,
            **dict(self.authority.artifact_identities()),
            "actual_bound_pathways_used": [
                {
                    **self._binding_record(binding),
                    "actual_stage_ids": list(
                        dict.fromkeys(
                            item.stage_id
                            for item in self._invocations
                            if item.binding_id == binding.binding_id
                            and item.claim_qualifying_effect
                        )
                    ),
                    "actual_symbol_ids": list(
                        dict.fromkeys(
                            item.symbol_id
                            for item in self._invocations
                            if item.binding_id == binding.binding_id
                            and item.claim_qualifying_effect
                        )
                    ),
                }
                for binding in sorted(actual_bindings, key=lambda item: item.binding_id)
            ],
            "actual_stage_symbol_invocations": actual_uses,
            "actual_composition_crossing_invocations": crossing_uses,
            "actual_candidate_mechanism_invocations": candidate_mechanism_uses,
            "execution_transcript_digest": transcript_digest,
            "execution_transcript_trust_requirement": (
                EXECUTION_TRANSCRIPT_TRUST_REQUIREMENT
            ),
            "composition_crossing_witnesses": list(composition_witnesses),
            "allowed_pathway_alternatives_actual_use": alternative_uses,
            "registered_compositions_exercised": [
                self._composition_record(binding) for binding in exercised_compositions
            ],
            "adapters_used": deepcopy(
                claim_envelope["required_qualifiers"]["adapter_cuts"]
            ),
            "producer_cuts_used": deepcopy(
                claim_envelope["required_qualifiers"]["producer_cuts"]
            ),
            "candidate_relations_exercised": [
                {
                    **self._candidates[item.candidate_id].to_record(),
                    "candidate_execution_witness": dict(item.execution_witness),
                }
                for item in self._candidate_uses
            ],
            "declared_but_unused": declared_but_unused,
            "effect_outcome_summary": {
                "stage_invocation_counts": {
                    outcome: sum(
                        item.effect_outcome == outcome for item in self._invocations
                    )
                    for outcome in sorted(EFFECT_OUTCOMES)
                },
                "claim_qualifying_stage_invocation_indices": [
                    index
                    for index, item in enumerate(self._invocations)
                    if item.claim_qualifying_effect
                ],
                "non_qualifying_returned_stage_invocation_indices": [
                    index
                    for index, item in enumerate(self._invocations)
                    if item.outcome == "returned"
                    and not item.claim_qualifying_effect
                ],
                "raised_stage_invocation_indices": [
                    index
                    for index, item in enumerate(self._invocations)
                    if item.outcome == "raised"
                ],
                "crossing_invocation_counts": {
                    outcome: sum(
                        item.effect_outcome == outcome
                        for item in self._crossing_invocations
                    )
                    for outcome in sorted(EFFECT_OUTCOMES)
                },
                "claim_qualifying_crossing_invocation_indices": [
                    index
                    for index, item in enumerate(self._crossing_invocations)
                    if item.claim_qualifying_effect
                ],
                "non_qualifying_returned_crossing_invocation_indices": [
                    index
                    for index, item in enumerate(self._crossing_invocations)
                    if item.outcome == "returned"
                    and not item.claim_qualifying_effect
                ],
                "raised_crossing_invocation_indices": [
                    index
                    for index, item in enumerate(self._crossing_invocations)
                    if item.outcome == "raised"
                ],
            },
            "pathway_use_graph": graph,
            "claim_envelope": claim_envelope,
            "blocked_claims": list(claim_envelope["blocked_claims"]),
            "undeclared_use_violations": [],
            "claim_qualified": bool(actual_bindings or self._candidate_uses),
            "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
            "whole_run_causal_closure_claimed": False,
            "untracked_execution_observable_by_binding_plane": False,
            "external_or_untracked_causal_input": UNTRACKED_EXECUTION_STATUS,
            "unbound_execution_accepted_as_evidence": False,
            "semantic_selection_performed_by_binder": False,
            "receipt_digest": "",
        }
        record["receipt_digest"] = canonical_digest(record, excluding="receipt_digest")
        receipt = BindingReceipt(record)
        self._phase = "sealed"
        return receipt

    def bind_pathway(
        self,
        pathway_id: str,
        *,
        stage_ids: Sequence[str] | None = None,
        binding_id: str | None = None,
    ) -> BoundPathway:
        """Declare one exact admitted pathway without choosing it for the caller."""

        self._require_declaration_phase()
        available_stages = self.authority.stage_ids(pathway_id)
        declared_stages = available_stages if stage_ids is None else tuple(stage_ids)
        if not declared_stages:
            raise CausalPathwayBindingError(
                "a pathway binding needs at least one stage"
            )
        unknown_stages = sorted(set(declared_stages) - set(available_stages))
        if unknown_stages:
            raise SymbolBindingError(
                f"pathway {pathway_id!r} has no stages {unknown_stages}"
            )
        identity = binding_id or f"pathway:{pathway_id}"
        if identity in self._pathway_bindings:
            raise CausalPathwayBindingError(f"duplicate binding ID {identity!r}")
        binding = BoundPathway(
            session=self,
            binding_id=identity,
            pathway_id=pathway_id,
            stage_ids=declared_stages,
        )
        self._pathway_bindings[identity] = binding
        return binding

    def bind_composition(
        self,
        composition_id: str,
        *,
        binding_id: str | None = None,
    ) -> BoundComposition:
        """Declare one exact registered executable composition."""

        self._require_declaration_phase()
        composition = self.authority.composition(composition_id)
        status = str(composition["composition_status"])
        if status not in EXECUTABLE_COMPOSITION_STATUSES:
            raise UnbindableCompositionError(
                f"composition {composition_id} has non-bindable status {status}; "
                "open a distinct candidate only for genuinely new experimental work"
            )
        identity = binding_id or f"composition:{composition_id}"
        if identity in self._composition_bindings:
            raise CausalPathwayBindingError(f"duplicate binding ID {identity!r}")
        from_id = str(composition["from_pathway_id"])
        to_id = str(composition["to_pathway_id"])
        endpoints: dict[str, BoundPathway] = {}
        endpoint_specs = (
            (
                from_id,
                tuple(str(item) for item in composition["from_stage_ids"]),
                "from",
            ),
            (to_id, tuple(str(item) for item in composition["to_stage_ids"]), "to"),
        )
        for pathway_id, stages, direction in endpoint_specs:
            if pathway_id in endpoints:
                combined = tuple(
                    dict.fromkeys((*endpoints[pathway_id].stage_ids, *stages))
                )
                endpoints[pathway_id] = BoundPathway(
                    session=self,
                    binding_id=f"{identity}:pathway:{pathway_id}",
                    pathway_id=pathway_id,
                    stage_ids=combined,
                    composition_ids=(composition_id,),
                )
                continue
            endpoints[pathway_id] = BoundPathway(
                session=self,
                binding_id=f"{identity}:{direction}:{pathway_id}",
                pathway_id=pathway_id,
                stage_ids=stages,
                composition_ids=(composition_id,),
            )
        binding = BoundComposition(
            session=self,
            binding_id=identity,
            composition=composition,
            endpoints=endpoints,
        )
        self._composition_bindings[identity] = binding
        return binding

    def declare_alternatives(
        self,
        *,
        alternative_set_id: str,
        pathway_ids: Sequence[str],
        selection_authority: str,
    ) -> AllowedPathwayAlternatives:
        """Declare allowable choices without making a choice."""

        self._require_declaration_phase()
        if not alternative_set_id or alternative_set_id in self._alternatives:
            raise CausalPathwayBindingError("alternative_set_id must be unique")
        unique_pathways = tuple(dict.fromkeys(str(item) for item in pathway_ids))
        if len(unique_pathways) < 2:
            raise CausalPathwayBindingError(
                "dynamic alternatives require at least two pathways"
            )
        for pathway_id in unique_pathways:
            self.authority.pathway(pathway_id)
        if not selection_authority:
            raise CausalPathwayBindingError("selection_authority must be explicit")
        declaration = AllowedPathwayAlternatives(
            _session=self,
            alternative_set_id=alternative_set_id,
            pathway_ids=unique_pathways,
            selection_authority=selection_authority,
        )
        self._alternatives[alternative_set_id] = declaration
        return declaration

    def declare_candidate(
        self,
        *,
        candidate_id: str,
        candidate_kind: str,
        purpose: str,
        owner: str,
        consumed_pathway_ids: Sequence[str] = (),
        consumed_composition_ids: Sequence[str] = (),
        proposed_source_pathway_id: str | None = None,
        proposed_target_pathway_id: str | None = None,
        proposed_relation: str | None = None,
        authority: Mapping[str, str] | None = None,
        producer_residue: Sequence[str] = (),
        adapter_residue: Sequence[str] = (),
        configured_residue: Sequence[str] = (),
        evidence_owner: str,
        mechanism_evidence: Mapping[str, Any] | None = None,
        invalid_relabel_relation_review: Mapping[str, Any] | None = None,
        trusted_relation_review_digest: str | None = None,
        blocked_claims: Sequence[str] = (),
    ) -> CandidateDeclaration:
        """Declare experimental work without altering admitted authorities."""

        self._require_declaration_phase()
        declaration, mechanism_handle = _build_candidate_declaration(
            session=self,
            authority_provider=self.authority,
            existing_candidate_ids=self._candidates,
            executable_composition_statuses=EXECUTABLE_COMPOSITION_STATUSES,
            candidate_id=candidate_id,
            candidate_kind=candidate_kind,
            purpose=purpose,
            owner=owner,
            consumed_pathway_ids=consumed_pathway_ids,
            consumed_composition_ids=consumed_composition_ids,
            proposed_source_pathway_id=proposed_source_pathway_id,
            proposed_target_pathway_id=proposed_target_pathway_id,
            proposed_relation=proposed_relation,
            authority=authority,
            producer_residue=producer_residue,
            adapter_residue=adapter_residue,
            configured_residue=configured_residue,
            evidence_owner=evidence_owner,
            mechanism_evidence=mechanism_evidence,
            invalid_relabel_relation_review=invalid_relabel_relation_review,
            trusted_relation_review_digest=trusted_relation_review_digest,
            blocked_claims=blocked_claims,
        )
        self._candidates[candidate_id] = declaration
        if mechanism_handle is not None:
            self._candidate_mechanism_handles[candidate_id] = mechanism_handle
        return declaration


def unbound_execution_classification() -> Mapping[str, Any]:
    """Return the mandatory provenance classification for legacy direct calls."""

    return MappingProxyType(
        {
            "causal_pathway_provenance": "unbound",
            "claim_qualified": False,
            "accepted_binding_receipt": False,
        }
    )
