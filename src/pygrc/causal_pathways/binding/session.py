"""Causal-pathway binding handles and session orchestration."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from .artifacts import (
    BindingLock,
    BindingReceipt,
    build_binding_lock,
    build_binding_receipt,
)
from .authority import CausalPathwayAuthority, UnknownPathwayError
from .candidates import (
    CandidateDeclaration,
    CandidateUseRecord,
    InvalidCandidateError,
    VerifiedCandidateMechanism,
    _build_candidate_declaration,
)
from .effects import _classify_returned_effect
from .identity import (
    CausalPathwayBindingError,
    CompositionCrossingBinding,
    SourceSymbolBinding,
    SymbolBindingError,
    _callable_bound_owner,
    _callable_definition,
    _CallableIdentityGuard,
    _VerifiedSourceFile,
)
from .scopes import (
    AllowedPathwayAlternatives,
    BindingStateError,
    CandidateExecutionScope,
    CandidateMechanismInvocationRecord,
    CompositionExecutionScope,
    CrossingInvocationRecord,
    CrossingResultReference,
    FlowDerivedInstanceReference,
    InvocationRecord,
    _RuntimeScopeState,
    composition_dataflow_contract,
)

EXECUTABLE_COMPOSITION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "lawful_native",
        "lawful_with_explicit_adapter",
        "diagnostic_only",
        "producer_mediated",
    }
)


class UnbindableCompositionError(CausalPathwayBindingError):
    """Raised when a registered row is missing or an invalid relabel."""


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
        instance: object
        | CrossingResultReference
        | FlowDerivedInstanceReference
        | None,
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
        self._runtime = session._runtime_scope_state()
        self._authority = session.authority
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

    def _assert_flow_contract_source(
        self,
        *,
        runtime: _RuntimeScopeState,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        composition_id: str,
    ) -> tuple[str, str]:
        """Validate this handle without exposing its private linkage fields."""

        if (
            self._runtime is not runtime
            or self._binding_id != binding_id
            or self._pathway_id != pathway_id
            or self._stage_id != stage_id
            or composition_id not in self._composition_ids
        ):
            raise SymbolBindingError(
                f"source handle is not the declared {composition_id!r} "
                "flow-contract source"
            )
        return self._binding_id, self._stage_id

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._runtime.authorize_invocation(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            stage_id=self._stage_id,
            symbol_id=self._symbol.symbol_id,
            composition_ids=self._composition_ids,
        )
        target, callable_identity = self._assert_current_callable()
        candidate_request_flow = self._runtime.candidate_target_request_flow(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            symbol_id=self._symbol.symbol_id,
            positional_arguments=args,
            keyword_arguments=kwargs,
        )
        effect_contract = self._authority.effect_outcome_contract(
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
            runtime_object_flow = self._runtime.observe_object_flow(
                target=target,
                arguments=bound_arguments,
                result=None,
            )
            runtime_object_flow = self._runtime.attach_flow_derivation(
                runtime_object_flow,
                self._instance_reference,
            )
            self._runtime.record_invocation(
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
        runtime_object_flow = self._runtime.observe_object_flow(
            target=target,
            arguments=bound_arguments,
            result=result,
        )
        runtime_object_flow = self._runtime.attach_flow_derivation(
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
            self._authority,
            self._symbol.symbol_id,
            result,
            target=target,
            pre_call_evidence=pre_call_effect_evidence,
        )
        self._runtime.record_invocation(
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
        self._runtime.record_invocation_result(
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
        self._runtime = session._runtime_scope_state()
        self._authority = session.authority
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
        scope = self._runtime.authorize_crossing(
            composition=self._composition,
            symbol_id=self.symbol_id,
        )
        target, callable_identity = self._assert_current_callable()
        effect_contract = self._authority.effect_outcome_contract(self.symbol_id)
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
            self._runtime.record_crossing_invocation(
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
            self._authority,
            self.symbol_id,
            result,
            target=target,
            pre_call_evidence=pre_call_effect_evidence,
        )
        self._runtime.record_crossing_invocation(
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
            object | CrossingResultReference | FlowDerivedInstanceReference | None
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
        source_binding_id, source_stage_id = source._assert_flow_contract_source(
            runtime=self._session._runtime_scope_state(),
            binding_id=self.source_binding.binding_id,
            pathway_id=self.source_binding.pathway_id,
            stage_id=contract["source_stage_id"],
            composition_id=self.composition_id,
        )
        return FlowDerivedInstanceReference(
            session=self._session,
            composition=self,
            source_binding_id=source_binding_id,
            target_binding_id=self.target_binding.binding_id,
            target_pathway_id=self.target_binding.pathway_id,
            source_stage_id=source_stage_id,
            source_symbol_id=source.symbol_id,
            target_stage_id=contract["target_stage_id"],
            source_port=contract["source_port"],
            target_port=contract["target_port"],
        )

    def evidence_scope(self) -> CompositionExecutionScope:
        """Return an explicit provenance-only scope for one crossing use."""

        return CompositionExecutionScope(session=self._session, composition=self)


@dataclass
class _SessionPhaseState:
    value: str = "declaration"


@dataclass
class _DeclarationState:
    pathway_bindings: dict[str, BoundPathway] = field(default_factory=dict)
    composition_bindings: dict[str, BoundComposition] = field(default_factory=dict)
    candidates: dict[str, CandidateDeclaration] = field(default_factory=dict)
    candidate_mechanism_handles: dict[str, VerifiedCandidateMechanism] = field(
        default_factory=dict
    )
    alternatives: dict[str, AllowedPathwayAlternatives] = field(default_factory=dict)


@dataclass
class _LinkState:
    symbols: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    instances: dict[
        tuple[str, str],
        object | CrossingResultReference | FlowDerivedInstanceReference | None,
    ] = field(default_factory=dict)
    crossings: dict[str, dict[str, Any]] = field(default_factory=dict)
    crossing_runtime: dict[
        str,
        tuple[object, CrossingResultReference],
    ] = field(default_factory=dict)


@dataclass
class _ArtifactState:
    candidate_uses: list[CandidateUseRecord] = field(default_factory=list)
    lock: BindingLock | None = None


@dataclass
class _IdentityCacheState:
    resolved_source_paths: dict[str, Path] = field(default_factory=dict)
    verified_source_files: dict[Path, _VerifiedSourceFile] = field(default_factory=dict)
    callable_identity_guards: dict[str, _CallableIdentityGuard] = field(
        default_factory=dict
    )


class PathwayBindingSession:
    """Explicit declaration and linkage session; it never selects semantics."""

    def __init__(self, authority: CausalPathwayAuthority) -> None:
        self.authority = authority
        self._phase_state = _SessionPhaseState()
        self._declarations = _DeclarationState()
        self._links = _LinkState()
        self._artifacts = _ArtifactState()
        self._runtime = _RuntimeScopeState(self)
        self._identity_cache = _IdentityCacheState()

    def _callable_identity_guard(
        self,
        symbol: SourceSymbolBinding,
        target: Callable[..., Any],
    ) -> _CallableIdentityGuard:
        """Fully verify a symbol once and return its session-level guard."""

        existing = self._identity_cache.callable_identity_guards.get(symbol.symbol_id)
        if existing is not None:
            if existing.symbol != symbol:
                raise SymbolBindingError(
                    f"binding symbol {symbol.symbol_id!r} has conflicting identities"
                )
            existing.assert_current(target)
            return existing

        definition, module, qualified_symbol = symbol._validated_definition(target)
        expected_source = self._identity_cache.resolved_source_paths.get(
            symbol.source_path
        )
        if expected_source is None:
            expected_source = (
                self.authority.repository_root / symbol.source_path
            ).resolve()
            self._identity_cache.resolved_source_paths[symbol.source_path] = (
                expected_source
            )
        source = symbol._resolved_source_path(
            definition,
            self.authority.repository_root,
            expected_source=expected_source,
        )
        source_file = self._identity_cache.verified_source_files.get(source)
        if source_file is None:
            source_file = _VerifiedSourceFile.verify(
                source,
                expected_sha256=symbol.source_sha256,
            )
            self._identity_cache.verified_source_files[source] = source_file
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
        self._identity_cache.callable_identity_guards[symbol.symbol_id] = guard
        return guard

    def _verified_source_file_records(
        self,
    ) -> Mapping[Path, _VerifiedSourceFile]:
        """Expose the read-only source-file cache for identity pressure tests."""

        return MappingProxyType(self._identity_cache.verified_source_files)

    @property
    def phase(self) -> str:
        return self._phase_state.value

    def _runtime_scope_state(self) -> _RuntimeScopeState:
        """Return the cohesive runtime ledger and scope collaborator."""

        return self._runtime

    def _candidate_runtime(self) -> _RuntimeScopeState:
        """Return the candidate mechanism's narrow runtime collaborator."""

        return self._runtime

    def _scope_composition_is_declared(
        self,
        composition: Any,
    ) -> bool:
        return (
            self._declarations.composition_bindings.get(composition.binding_id)
            is composition
        )

    def _scope_candidate_is_declared(
        self,
        candidate: CandidateDeclaration,
    ) -> bool:
        return self._declarations.candidates.get(candidate.candidate_id) is candidate

    def _scope_alternatives_are_declared(
        self,
        alternatives: AllowedPathwayAlternatives,
    ) -> bool:
        return (
            self._declarations.alternatives.get(alternatives.alternative_set_id)
            is alternatives
        )

    @property
    def invocation_records(self) -> tuple[InvocationRecord, ...]:
        return self._runtime.invocations

    @property
    def crossing_invocation_records(self) -> tuple[CrossingInvocationRecord, ...]:
        return self._runtime.crossing_invocations

    @property
    def candidate_mechanism_invocation_records(
        self,
    ) -> tuple[CandidateMechanismInvocationRecord, ...]:
        return self._runtime.candidate_mechanism_invocations

    @property
    def candidates(self) -> tuple[CandidateDeclaration, ...]:
        return tuple(self._declarations.candidates.values())

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
            return self._declarations.candidate_mechanism_handles[candidate_id]
        except KeyError as exc:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} lacks executable mechanism evidence"
            ) from exc

    @property
    def alternatives(self) -> tuple[AllowedPathwayAlternatives, ...]:
        return tuple(self._declarations.alternatives.values())

    @property
    def binding_lock(self) -> BindingLock | None:
        return self._artifacts.lock

    def _require_declaration_phase(self) -> None:
        if self._phase_state.value != "declaration":
            raise BindingStateError(
                f"binding declarations are closed in session phase {self._phase_state.value!r}"
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
            object | CrossingResultReference | FlowDerivedInstanceReference | None
        ),
        callable_identity: Mapping[str, Any],
    ) -> None:
        self._require_declaration_phase()
        key = (binding_id, symbol.symbol_id)
        effect_contract = self.authority.effect_outcome_contract(symbol.symbol_id)
        runtime_instance_binding = self._runtime.runtime_instance_binding(
            instance,
            call_kind=symbol.call_kind,
        )
        self._links.symbols[key] = {
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
        self._links.instances[key] = instance

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
        if composition.binding_id in self._links.crossings:
            raise CausalPathwayBindingError(
                f"composition binding {composition.binding_id!r} already has a crossing"
            )
        symbol = crossing.symbol
        effect_contract = self.authority.effect_outcome_contract(symbol.symbol_id)
        self._links.crossings[composition.binding_id] = {
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
        self._links.crossing_runtime[composition.binding_id] = (
            source_instance,
            result_reference,
        )

    def _all_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        endpoints = (
            endpoint
            for composition in self._declarations.composition_bindings.values()
            for endpoint in composition.endpoint_bindings
        )
        return (*self._declarations.pathway_bindings.values(), *endpoints)

    def _validate_explicit_crossing_dataflow(self) -> None:
        """Bind explicit-adapter endpoints to the adapter's exact object flow."""

        for composition in self._declarations.composition_bindings.values():
            if composition.composition_status != "lawful_with_explicit_adapter":
                continue
            try:
                source_instance, result_reference = self._links.crossing_runtime[
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
                for key, link in self._links.symbols.items():
                    if key[0] != endpoint.binding_id:
                        continue
                    if link["call_kind"] != "instance_method":
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            "requires instance-bound stage symbols"
                        )
                    if self._links.instances.get(key) is not expected_instance:
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            f"must use its {role.replace('_', ' ')}"
                        )
                    link["composition_crossing_instance_role"] = role
            crossing_link = self._links.crossings[composition.binding_id]
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
            for binding in self._declarations.composition_bindings.values()
            if binding.composition_status == "lawful_with_explicit_adapter"
            and binding.binding_id not in self._links.crossings
        )
        if missing_crossings:
            raise BindingStateError(
                "explicit-adapter compositions require their exact crossing "
                f"callable before lock: {missing_crossings}"
            )
        self._validate_explicit_crossing_dataflow()
        for candidate in self._declarations.candidates.values():
            if candidate.mechanism_evidence is not None:
                candidate.mechanism_evidence.assert_current(
                    self.authority.repository_root,
                    candidate_kind=candidate.candidate_kind,
                    proposed_source_pathway_id=(candidate.proposed_source_pathway_id),
                    proposed_target_pathway_id=(candidate.proposed_target_pathway_id),
                    proposed_relation=candidate.proposed_relation,
                )
        declared_pathway_ids = {binding.pathway_id for binding in bindings}
        for alternatives in self._declarations.alternatives.values():
            missing = sorted(set(alternatives.pathway_ids) - declared_pathway_ids)
            if missing:
                raise BindingStateError(
                    f"alternative set {alternatives.alternative_set_id!r} lacks "
                    f"declared pathway bindings for {missing}"
                )
        self._artifacts.lock = build_binding_lock(
            authority=self.authority,
            bindings=bindings,
            composition_bindings=tuple(
                self._declarations.composition_bindings.values()
            ),
            alternatives=tuple(self._declarations.alternatives.values()),
            candidates=tuple(self._declarations.candidates.values()),
            linked_symbols=self._links.symbols,
            crossing_links=self._links.crossings,
        )
        self._phase_state.value = "locked"
        return self._artifacts.lock

    def record_candidate_use(
        self,
        candidate_id: str,
    ) -> CandidateUseRecord:
        """Record one scoped use of the frozen candidate executable."""

        if self._phase_state.value != "locked":
            raise BindingStateError("candidate use requires a frozen binding lock")
        if candidate_id not in self._declarations.candidates:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} was not declared before lock"
            )
        if any(
            item.candidate_id == candidate_id for item in self._artifacts.candidate_uses
        ):
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} already has a use record"
            )
        candidate = self._declarations.candidates[candidate_id]
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
        witnesses = self._runtime.candidate_witnesses(candidate)
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
        self._artifacts.candidate_uses.append(use)
        return use

    def _composition_witnesses(self) -> tuple[dict[str, Any], ...]:
        return self._runtime.composition_witnesses()

    def _alternative_selection_witnesses(self) -> tuple[dict[str, Any], ...]:
        return self._runtime.alternative_selection_witnesses()

    def _exercised_compositions(
        self,
        witnesses: Sequence[Mapping[str, Any]],
    ) -> tuple[BoundComposition, ...]:
        witnessed_binding_ids = {str(witness["binding_id"]) for witness in witnesses}
        return tuple(
            binding
            for binding in self._declarations.composition_bindings.values()
            if binding.binding_id in witnessed_binding_ids
        )

    def _actual_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        successful_binding_ids = {
            record.binding_id
            for record in self._runtime.invocations
            if record.claim_qualifying_effect
        }
        return tuple(
            binding
            for binding in self._all_pathway_bindings()
            if binding.binding_id in successful_binding_ids
        )

    def build_receipt(self) -> BindingReceipt:
        """Seal actual use against the exact frozen binding lock."""

        if self._phase_state.value != "locked" or self._artifacts.lock is None:
            raise BindingStateError("a receipt requires one active binding lock")
        self._runtime.assert_no_active_scopes()
        self.authority.assert_current()
        actual_bindings = self._actual_pathway_bindings()
        composition_witnesses = self._composition_witnesses()
        alternative_selection_witnesses = self._alternative_selection_witnesses()
        exercised_compositions = self._exercised_compositions(composition_witnesses)
        used_candidate_ids = {
            item.candidate_id for item in self._artifacts.candidate_uses
        }
        used_candidates = tuple(
            self._declarations.candidates[candidate_id]
            for candidate_id in sorted(used_candidate_ids)
        )
        witnessed_candidate_mechanisms = {
            int(item.execution_witness["candidate_mechanism_invocation_index"])
            for item in self._artifacts.candidate_uses
        }
        returned_candidate_mechanisms = {
            index
            for index, item in enumerate(self._runtime.candidate_mechanism_invocations)
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
                proposed_source_pathway_id=(candidate.proposed_source_pathway_id),
                proposed_target_pathway_id=(candidate.proposed_target_pathway_id),
                proposed_relation=candidate.proposed_relation,
            )
        receipt = build_binding_receipt(
            authority=self.authority,
            lock=self._artifacts.lock,
            all_bindings=self._all_pathway_bindings(),
            actual_bindings=actual_bindings,
            composition_bindings=tuple(
                self._declarations.composition_bindings.values()
            ),
            exercised_compositions=exercised_compositions,
            candidates=self._declarations.candidates,
            candidate_uses=tuple(self._artifacts.candidate_uses),
            alternatives=tuple(self._declarations.alternatives.values()),
            linked_symbols=self._links.symbols,
            crossing_links=self._links.crossings,
            invocations=self._runtime.invocations,
            crossing_invocations=self._runtime.crossing_invocations,
            candidate_mechanism_invocations=(
                self._runtime.candidate_mechanism_invocations
            ),
            composition_witnesses=composition_witnesses,
            alternative_selection_witnesses=alternative_selection_witnesses,
        )
        self._phase_state.value = "sealed"
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
        if identity in self._declarations.pathway_bindings:
            raise CausalPathwayBindingError(f"duplicate binding ID {identity!r}")
        binding = BoundPathway(
            session=self,
            binding_id=identity,
            pathway_id=pathway_id,
            stage_ids=declared_stages,
        )
        self._declarations.pathway_bindings[identity] = binding
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
        if identity in self._declarations.composition_bindings:
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
        self._declarations.composition_bindings[identity] = binding
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
        if (
            not alternative_set_id
            or alternative_set_id in self._declarations.alternatives
        ):
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
        self._declarations.alternatives[alternative_set_id] = declaration
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
            existing_candidate_ids=self._declarations.candidates,
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
        self._declarations.candidates[candidate_id] = declaration
        if mechanism_handle is not None:
            self._declarations.candidate_mechanism_handles[candidate_id] = (
                mechanism_handle
            )
        return declaration


__all__ = [
    "EXECUTABLE_COMPOSITION_STATUSES",
    "BoundComposition",
    "BoundPathway",
    "PathwayBindingSession",
    "UnbindableCompositionError",
    "VerifiedCallable",
    "VerifiedCompositionCrossing",
]
