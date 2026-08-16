"""Exact causal-pathway linkage for evidence-bearing consumers.

This module links declared knowledge-plane identities to current Python
callables.  It deliberately does not select pathways or dispatch causal work.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, cast

AUTHORITY_PATHS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "registry": "specs/grc-lgrc-causal-pathway-contracts.json",
        "crosswalk": "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json",
        "matrix": "specs/grc-lgrc-causal-pathway-composition-matrix.json",
        "selector": "specs/grc-lgrc-causal-pathway-selection-guide.json",
        "policy": "specs/grc-lgrc-causal-pathway-conformance.json",
        "bindings": "specs/grc-lgrc-causal-pathway-bindings.json",
    }
)

EXECUTABLE_COMPOSITION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "lawful_native",
        "lawful_with_explicit_adapter",
        "diagnostic_only",
        "producer_mediated",
    }
)

AUTHORITY_COORDINATES: Final[tuple[str, ...]] = (
    "direction",
    "funding",
    "eligibility",
    "scheduling",
    "commit",
    "reception",
)


class CausalPathwayBindingError(ValueError):
    """Base error for fail-closed binding operations."""


class AuthorityDriftError(CausalPathwayBindingError):
    """Raised when a knowledge or source-link authority no longer matches."""


class UnknownPathwayError(CausalPathwayBindingError):
    """Raised when a pathway is absent from the admitted registry."""


class UnknownCompositionError(CausalPathwayBindingError):
    """Raised when a composition is absent from the admitted matrix."""


class UnbindableCompositionError(CausalPathwayBindingError):
    """Raised when a registered row is missing or an invalid relabel."""


class InvalidCandidateError(CausalPathwayBindingError):
    """Raised when an unregistered candidate hides identity or authority debt."""


class SymbolBindingError(CausalPathwayBindingError):
    """Raised when an exact stage symbol cannot be linked safely."""


class BindingStateError(CausalPathwayBindingError):
    """Raised when declaration, locking, use, and sealing order is violated."""


def canonical_digest(value: Mapping[str, Any], *, excluding: str) -> str:
    """Return the repository's canonical SHA-256 digest for one JSON object."""

    payload = {key: item for key, item in value.items() if key != excluding}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuthorityDriftError(f"authority {path} must contain a JSON object")
    return value


def _index_unique(
    records: Iterable[Mapping[str, Any]],
    *,
    key: str,
    authority_name: str,
) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for record in records:
        identity = str(record.get(key, ""))
        if not identity or identity in index:
            raise AuthorityDriftError(
                f"{authority_name} has a missing or duplicate {key}: {identity!r}"
            )
        index[identity] = record
    return index


@dataclass(frozen=True)
class SourceSymbolBinding:
    """One exact stage-to-source link from the machine binding map."""

    symbol_id: str
    module: str
    qualified_symbol: str
    binding_role: str
    call_kind: str
    source_path: str
    source_sha256: str
    required_keyword_arguments: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> SourceSymbolBinding:
        required = record.get("required_keyword_arguments", {})
        if not isinstance(required, Mapping):
            raise AuthorityDriftError("required_keyword_arguments must be a mapping")
        return cls(
            symbol_id=str(record["symbol_id"]),
            module=str(record["module"]),
            qualified_symbol=str(record["qualified_symbol"]),
            binding_role=str(record["binding_role"]),
            call_kind=str(record["call_kind"]),
            source_path=str(record["source_path"]),
            source_sha256=str(record["source_sha256"]),
            required_keyword_arguments=MappingProxyType(dict(required)),
        )

    def resolve(self) -> Callable[..., Any]:
        """Import the exact callable recorded by this link."""

        target: Any = importlib.import_module(self.module)
        try:
            for part in self.qualified_symbol.split("."):
                target = getattr(target, part)
        except AttributeError as exc:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} no longer resolves"
            ) from exc
        if not callable(target):
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} is no longer callable"
            )
        return cast(Callable[..., Any], target)


@dataclass(frozen=True)
class CandidateDeclaration:
    """An explicit unregistered pathway or composition candidate."""

    candidate_id: str
    candidate_kind: str
    purpose: str
    owner: str
    consumed_pathway_ids: tuple[str, ...]
    consumed_composition_ids: tuple[str, ...]
    proposed_source_pathway_id: str | None
    proposed_target_pathway_id: str | None
    proposed_relation: str | None
    authority: Mapping[str, str]
    producer_residue: tuple[str, ...]
    adapter_residue: tuple[str, ...]
    configured_residue: tuple[str, ...]
    evidence_owner: str
    blocked_claims: tuple[str, ...]
    claim_ceiling: str = "experimental_unregistered"
    promotion_status: str = "none"

    def to_record(self) -> dict[str, Any]:
        """Return a serializable candidate record."""

        return {
            "candidate_id": self.candidate_id,
            "candidate_kind": self.candidate_kind,
            "purpose": self.purpose,
            "owner": self.owner,
            "consumed_admitted_pathway_ids": list(self.consumed_pathway_ids),
            "consumed_admitted_composition_ids": list(self.consumed_composition_ids),
            "proposed_source_pathway_id": self.proposed_source_pathway_id,
            "proposed_target_pathway_id": self.proposed_target_pathway_id,
            "proposed_relation": self.proposed_relation,
            "authority": dict(self.authority),
            "producer_residue": list(self.producer_residue),
            "adapter_residue": list(self.adapter_residue),
            "configured_residue": list(self.configured_residue),
            "evidence_owner": self.evidence_owner,
            "claim_ceiling": self.claim_ceiling,
            "blocked_claims": list(self.blocked_claims),
            "promotion_status": self.promotion_status,
        }


@dataclass(frozen=True)
class AllowedPathwayAlternatives:
    """Declared dynamic alternatives; it contains no selection operation."""

    alternative_set_id: str
    pathway_ids: tuple[str, ...]
    selection_authority: str


class CausalPathwayAuthority:
    """Validated immutable view over accepted knowledge and binding artifacts."""

    def __init__(
        self,
        *,
        repository_root: Path,
        documents: Mapping[str, Mapping[str, Any]],
        pathways: Mapping[str, Mapping[str, Any]],
        compositions: Mapping[str, Mapping[str, Any]],
        stage_symbols: Mapping[tuple[str, str], tuple[SourceSymbolBinding, ...]],
    ) -> None:
        self._repository_root = repository_root
        self._documents = MappingProxyType(dict(documents))
        self._pathways = MappingProxyType(dict(pathways))
        self._compositions = MappingProxyType(dict(compositions))
        self._stage_symbols = MappingProxyType(dict(stage_symbols))

    @property
    def repository_root(self) -> Path:
        return self._repository_root

    @property
    def registry_digest(self) -> str:
        return str(self._documents["registry"]["registry_digest"])

    @property
    def crosswalk_digest(self) -> str:
        return str(self._documents["crosswalk"]["crosswalk_digest"])

    @property
    def matrix_digest(self) -> str:
        return str(self._documents["matrix"]["matrix_digest"])

    @property
    def selector_digest(self) -> str:
        return str(self._documents["selector"]["selector_digest"])

    @property
    def policy_digest(self) -> str:
        return str(self._documents["policy"]["policy_digest"])

    @property
    def binding_map_digest(self) -> str:
        return str(self._documents["bindings"]["binding_map_digest"])

    @property
    def source_revision(self) -> str:
        return str(self._documents["bindings"]["source_revision"])

    def artifact_identities(self) -> Mapping[str, str]:
        """Return the accepted digests consumed by one binding lock."""

        return MappingProxyType(
            {
                "source_revision": self.source_revision,
                "registry_digest": self.registry_digest,
                "crosswalk_digest": self.crosswalk_digest,
                "matrix_digest": self.matrix_digest,
                "selector_digest": self.selector_digest,
                "binding_map_digest": self.binding_map_digest,
                "conformance_policy_digest": self.policy_digest,
            }
        )

    def assert_current(self) -> None:
        """Fail closed if any consumed authority or source link has drifted."""

        current = type(self).load(self.repository_root)
        if dict(current.artifact_identities()) != dict(self.artifact_identities()):
            raise AuthorityDriftError(
                "loaded causal-pathway authority is no longer current"
            )

    def pathway(self, pathway_id: str) -> Mapping[str, Any]:
        try:
            return deepcopy(self._pathways[pathway_id])
        except KeyError as exc:
            raise UnknownPathwayError(
                f"pathway {pathway_id!r} is not admitted; declare a candidate instead"
            ) from exc

    def composition(self, composition_id: str) -> Mapping[str, Any]:
        try:
            return deepcopy(self._compositions[composition_id])
        except KeyError as exc:
            raise UnknownCompositionError(
                f"composition {composition_id!r} is not registered; "
                "declare a candidate instead"
            ) from exc

    def stage_ids(self, pathway_id: str) -> tuple[str, ...]:
        pathway = self.pathway(pathway_id)
        return tuple(str(stage["stage_id"]) for stage in pathway["stage_sequence"])

    def symbols(
        self,
        pathway_id: str,
        stage_id: str,
    ) -> tuple[SourceSymbolBinding, ...]:
        self.pathway(pathway_id)
        try:
            return self._stage_symbols[(pathway_id, stage_id)]
        except KeyError as exc:
            raise SymbolBindingError(
                f"stage {pathway_id}:{stage_id} has no current binding"
            ) from exc

    @classmethod
    def load(cls, repository_root: str | Path) -> CausalPathwayAuthority:
        """Load and validate all accepted knowledge and linkage artifacts."""

        root = Path(repository_root).resolve()
        documents = {
            name: _load_json(root / relative)
            for name, relative in AUTHORITY_PATHS.items()
        }
        digest_fields = {
            "registry": "registry_digest",
            "crosswalk": "crosswalk_digest",
            "matrix": "matrix_digest",
            "selector": "selector_digest",
            "policy": "policy_digest",
            "bindings": "binding_map_digest",
        }
        for name, digest_field in digest_fields.items():
            actual = canonical_digest(documents[name], excluding=digest_field)
            expected = str(documents[name].get(digest_field, ""))
            if actual != expected:
                raise AuthorityDriftError(
                    f"{name} digest mismatch: expected {expected}, got {actual}"
                )

        bindings = documents["bindings"]
        consumed_digests = {
            "registry_digest": documents["registry"]["registry_digest"],
            "crosswalk_digest": documents["crosswalk"]["crosswalk_digest"],
            "matrix_digest": documents["matrix"]["matrix_digest"],
            "selector_digest": documents["selector"]["selector_digest"],
            "policy_digest": documents["policy"]["policy_digest"],
        }
        for field_name, actual in consumed_digests.items():
            if bindings.get(field_name) != actual:
                raise AuthorityDriftError(f"binding map consumes stale {field_name}")

        pathways = _index_unique(
            documents["registry"]["pathways"],
            key="pathway_id",
            authority_name="registry",
        )
        compositions = _index_unique(
            documents["matrix"]["compositions"],
            key="composition_id",
            authority_name="matrix",
        )
        expected_stages = {
            (pathway_id, str(stage["stage_id"]))
            for pathway_id, pathway in pathways.items()
            for stage in pathway["stage_sequence"]
        }
        stage_symbols: dict[tuple[str, str], tuple[SourceSymbolBinding, ...]] = {}
        symbol_ids: set[str] = set()
        for stage_record in bindings["stage_bindings"]:
            key = (
                str(stage_record["pathway_id"]),
                str(stage_record["stage_id"]),
            )
            if key in stage_symbols:
                raise AuthorityDriftError(f"duplicate binding stage {key}")
            symbols = tuple(
                SourceSymbolBinding.from_record(record)
                for record in stage_record["symbols"]
            )
            if not symbols:
                raise AuthorityDriftError(f"binding stage {key} has no symbols")
            for symbol in symbols:
                if symbol.symbol_id in symbol_ids:
                    raise AuthorityDriftError(
                        f"duplicate binding symbol {symbol.symbol_id!r}"
                    )
                symbol_ids.add(symbol.symbol_id)
                source_path = root / symbol.source_path
                if not source_path.is_file():
                    raise AuthorityDriftError(
                        f"binding source is absent: {symbol.source_path}"
                    )
                if sha256_file(source_path) != symbol.source_sha256:
                    raise AuthorityDriftError(
                        f"binding source is stale: {symbol.source_path}"
                    )
                symbol.resolve()
            stage_symbols[key] = symbols
        if set(stage_symbols) != expected_stages:
            missing = sorted(expected_stages - set(stage_symbols))
            extra = sorted(set(stage_symbols) - expected_stages)
            raise AuthorityDriftError(
                f"binding map stage closure mismatch; missing={missing}, extra={extra}"
            )
        if int(bindings["pathway_count"]) != len(pathways):
            raise AuthorityDriftError("binding-map pathway count is stale")
        if int(bindings["stage_binding_count"]) != len(stage_symbols):
            raise AuthorityDriftError("binding-map stage count is stale")
        return cls(
            repository_root=root,
            documents=documents,
            pathways=pathways,
            compositions=compositions,
            stage_symbols=stage_symbols,
        )


@dataclass(frozen=True)
class InvocationRecord:
    """One in-memory I113 use record around real-callable delegation."""

    binding_id: str
    pathway_id: str
    stage_id: str
    symbol_id: str
    composition_ids: tuple[str, ...]
    outcome: str
    result_type: str | None
    error_type: str | None


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
        instance: object | None,
    ) -> None:
        target = symbol.resolve()
        if instance is not None:
            if symbol.call_kind != "instance_method":
                raise SymbolBindingError(
                    f"{symbol.symbol_id!r} is not an instance method"
                )
            target = target.__get__(instance, type(instance))
        self._session = session
        self._binding_id = binding_id
        self._pathway_id = pathway_id
        self._stage_id = stage_id
        self._composition_ids = composition_ids
        self._symbol = symbol
        self._target = target
        self.__name__ = getattr(target, "__name__", symbol.qualified_symbol)
        self.__doc__ = getattr(target, "__doc__", None)
        self.__signature__ = inspect.signature(target)

    @property
    def symbol_id(self) -> str:
        return self._symbol.symbol_id

    @property
    def linked_callable(self) -> Callable[..., Any]:
        return self._target

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._session._assert_invocation_allowed(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            stage_id=self._stage_id,
            symbol_id=self._symbol.symbol_id,
            composition_ids=self._composition_ids,
        )
        for name, expected in self._symbol.required_keyword_arguments.items():
            if kwargs.get(name) != expected:
                raise SymbolBindingError(
                    f"binding {self._symbol.symbol_id!r} requires {name}={expected!r}"
                )
        try:
            result = self._target(*args, **kwargs)
        except Exception as exc:
            self._session._record_invocation(
                InvocationRecord(
                    binding_id=self._binding_id,
                    pathway_id=self._pathway_id,
                    stage_id=self._stage_id,
                    symbol_id=self._symbol.symbol_id,
                    composition_ids=self._composition_ids,
                    outcome="raised",
                    result_type=None,
                    error_type=type(exc).__name__,
                )
            )
            raise
        self._session._record_invocation(
            InvocationRecord(
                binding_id=self._binding_id,
                pathway_id=self._pathway_id,
                stage_id=self._stage_id,
                symbol_id=self._symbol.symbol_id,
                composition_ids=self._composition_ids,
                outcome="returned",
                result_type=type(result).__name__,
                error_type=None,
            )
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
        instance: object | None = None,
    ) -> VerifiedCallable:
        """Link one declared stage to an exact real source callable."""

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
        self._session._register_link(
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
        )
        return VerifiedCallable(
            session=self._session,
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
            instance=instance,
        )


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

    def pathway(self, pathway_id: str) -> BoundPathway:
        try:
            return self._endpoints[pathway_id]
        except KeyError as exc:
            raise UnknownPathwayError(
                f"{pathway_id!r} is not an endpoint of {self.composition_id}"
            ) from exc


@dataclass(frozen=True)
class CandidateUseRecord:
    """Explicit evidence that a declared candidate relation was exercised."""

    candidate_id: str
    evidence_reference: str


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
        self._alternatives: dict[str, AllowedPathwayAlternatives] = {}
        self._linked_symbols: dict[tuple[str, str], dict[str, Any]] = {}
        self._invocations: list[InvocationRecord] = []
        self._candidate_uses: list[CandidateUseRecord] = []
        self._lock: BindingLock | None = None

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def invocation_records(self) -> tuple[InvocationRecord, ...]:
        return tuple(self._invocations)

    @property
    def candidates(self) -> tuple[CandidateDeclaration, ...]:
        return tuple(self._candidates.values())

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
    ) -> None:
        self._require_declaration_phase()
        key = (binding_id, symbol.symbol_id)
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
        }

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

    def _record_invocation(self, record: InvocationRecord) -> None:
        self._invocations.append(record)

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
            composition_bindings, key=lambda item: item.composition_id
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

        candidate_records = [candidate.to_record() for candidate in candidates]
        for candidate in candidates:
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

    def freeze_lock(self) -> BindingLock:
        """Close declarations and freeze exact symbols before execution."""

        self._require_declaration_phase()
        self.authority.assert_current()
        bindings = self._all_pathway_bindings()
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
        *,
        evidence_reference: str,
    ) -> CandidateUseRecord:
        """Record explicit candidate use without promoting or executing it."""

        if self._phase != "locked":
            raise BindingStateError("candidate use requires a frozen binding lock")
        if candidate_id not in self._candidates:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} was not declared before lock"
            )
        if not evidence_reference:
            raise InvalidCandidateError("candidate use needs an evidence reference")
        if any(item.candidate_id == candidate_id for item in self._candidate_uses):
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} already has a use record"
            )
        use = CandidateUseRecord(
            candidate_id=candidate_id,
            evidence_reference=evidence_reference,
        )
        self._candidate_uses.append(use)
        return use

    def _exercised_compositions(self) -> tuple[BoundComposition, ...]:
        successful_stages = {
            (record.pathway_id, record.stage_id, composition_id)
            for record in self._invocations
            if record.outcome == "returned"
            for composition_id in record.composition_ids
        }
        exercised: list[BoundComposition] = []
        for binding in self._composition_bindings.values():
            contract = binding.contract
            required = {
                *(
                    (
                        str(contract["from_pathway_id"]),
                        str(stage_id),
                        binding.composition_id,
                    )
                    for stage_id in contract["from_stage_ids"]
                ),
                *(
                    (
                        str(contract["to_pathway_id"]),
                        str(stage_id),
                        binding.composition_id,
                    )
                    for stage_id in contract["to_stage_ids"]
                ),
            }
            if required <= successful_stages:
                exercised.append(binding)
        return tuple(exercised)

    def _actual_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        successful_binding_ids = {
            record.binding_id
            for record in self._invocations
            if record.outcome == "returned"
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
            record for record in self._invocations if record.outcome == "returned"
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
                        "evidence_reference": use.evidence_reference,
                        "authority": dict(candidate.authority),
                        "producer_residue": list(candidate.producer_residue),
                        "adapter_residue": list(candidate.adapter_residue),
                        "configured_residue": list(candidate.configured_residue),
                        "blocked_claims": list(candidate.blocked_claims),
                    }
                )
                continue
            assert candidate.proposed_source_pathway_id is not None
            assert candidate.proposed_target_pathway_id is not None
            if (
                candidate.proposed_source_pathway_id not in actual_by_pathway
                or candidate.proposed_target_pathway_id not in actual_by_pathway
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
                    "source_node_id": actual_by_pathway[
                        candidate.proposed_source_pathway_id
                    ],
                    "target_node_id": actual_by_pathway[
                        candidate.proposed_target_pathway_id
                    ],
                    "proposed_relation": candidate.proposed_relation,
                    "claim_ceiling": candidate.claim_ceiling,
                    "promotion_status": candidate.promotion_status,
                    "evidence_reference": use.evidence_reference,
                    "authority": dict(candidate.authority),
                    "producer_residue": list(candidate.producer_residue),
                    "adapter_residue": list(candidate.adapter_residue),
                    "configured_residue": list(candidate.configured_residue),
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
        self.authority.assert_current()
        actual_bindings = self._actual_pathway_bindings()
        exercised_compositions = self._exercised_compositions()
        used_candidate_ids = {item.candidate_id for item in self._candidate_uses}
        used_candidates = tuple(
            self._candidates[candidate_id]
            for candidate_id in sorted(used_candidate_ids)
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
                "result_type": item.result_type,
                "error_type": item.error_type,
            }
            for index, item in enumerate(self._invocations)
        ]
        alternative_uses = [
            {
                "alternative_set_id": alternatives.alternative_set_id,
                "selection_authority": alternatives.selection_authority,
                "allowed_pathway_ids": list(alternatives.pathway_ids),
                "actual_pathway_ids_used": [
                    pathway_id
                    for pathway_id in alternatives.pathway_ids
                    if any(
                        binding.pathway_id == pathway_id for binding in actual_bindings
                    )
                ],
            }
            for alternatives in sorted(
                self._alternatives.values(),
                key=lambda item: item.alternative_set_id,
            )
        ]
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
                            and item.outcome == "returned"
                        )
                    ),
                    "actual_symbol_ids": list(
                        dict.fromkeys(
                            item.symbol_id
                            for item in self._invocations
                            if item.binding_id == binding.binding_id
                            and item.outcome == "returned"
                        )
                    ),
                }
                for binding in sorted(actual_bindings, key=lambda item: item.binding_id)
            ],
            "actual_stage_symbol_invocations": actual_uses,
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
                    "evidence_reference": item.evidence_reference,
                }
                for item in self._candidate_uses
            ],
            "declared_but_unused": declared_but_unused,
            "pathway_use_graph": graph,
            "claim_envelope": claim_envelope,
            "blocked_claims": list(claim_envelope["blocked_claims"]),
            "undeclared_use_violations": [],
            "claim_qualified": bool(actual_bindings or self._candidate_uses),
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
        blocked_claims: Sequence[str] = (),
    ) -> CandidateDeclaration:
        """Declare experimental work without altering admitted authorities."""

        self._require_declaration_phase()
        if not candidate_id or candidate_id in self._candidates:
            raise InvalidCandidateError("candidate_id must be non-empty and unique")
        try:
            self.authority.pathway(candidate_id)
        except UnknownPathwayError:
            pass
        else:
            raise InvalidCandidateError(
                "candidate ID collides with an admitted pathway"
            )
        try:
            self.authority.composition(candidate_id)
        except UnknownCompositionError:
            pass
        else:
            raise InvalidCandidateError(
                "candidate ID collides with a registered composition"
            )
        if candidate_kind not in {"pathway", "composition"}:
            raise InvalidCandidateError("candidate_kind must be pathway or composition")
        if not purpose or not owner or not evidence_owner:
            raise InvalidCandidateError(
                "purpose, owner, and evidence_owner are required"
            )
        consumed_pathways = tuple(dict.fromkeys(consumed_pathway_ids))
        consumed_compositions = tuple(dict.fromkeys(consumed_composition_ids))
        for pathway_id in consumed_pathways:
            self.authority.pathway(pathway_id)
        for composition_id in consumed_compositions:
            composition = self.authority.composition(composition_id)
            if composition["composition_status"] not in EXECUTABLE_COMPOSITION_STATUSES:
                raise InvalidCandidateError(
                    f"candidate cannot consume non-executable composition {composition_id}"
                )
        if candidate_kind == "composition":
            if not proposed_source_pathway_id or not proposed_target_pathway_id:
                raise InvalidCandidateError(
                    "composition candidates require explicit source and target pathways"
                )
            self.authority.pathway(proposed_source_pathway_id)
            self.authority.pathway(proposed_target_pathway_id)
            if not proposed_relation:
                raise InvalidCandidateError(
                    "composition candidate requires a genuinely new relation description"
                )
        raw_authority = dict(authority or {})
        unknown_coordinates = sorted(set(raw_authority) - set(AUTHORITY_COORDINATES))
        if unknown_coordinates:
            raise InvalidCandidateError(
                f"unknown authority coordinates: {unknown_coordinates}"
            )
        resolved_authority = {
            coordinate: str(raw_authority.get(coordinate) or "unresolved")
            for coordinate in AUTHORITY_COORDINATES
        }
        blocked = tuple(
            dict.fromkeys(
                (
                    *blocked_claims,
                    "candidate relation is admitted",
                    "candidate relation is native",
                    "candidate declaration is promotion",
                )
            )
        )
        declaration = CandidateDeclaration(
            candidate_id=candidate_id,
            candidate_kind=candidate_kind,
            purpose=purpose,
            owner=owner,
            consumed_pathway_ids=consumed_pathways,
            consumed_composition_ids=consumed_compositions,
            proposed_source_pathway_id=proposed_source_pathway_id,
            proposed_target_pathway_id=proposed_target_pathway_id,
            proposed_relation=proposed_relation,
            authority=MappingProxyType(resolved_authority),
            producer_residue=tuple(producer_residue),
            adapter_residue=tuple(adapter_residue),
            configured_residue=tuple(configured_residue),
            evidence_owner=evidence_owner,
            blocked_claims=blocked,
        )
        self._candidates[candidate_id] = declaration
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
